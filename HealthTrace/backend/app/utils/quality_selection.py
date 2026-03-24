"""
Strategia Data Quality-Based per selezione dati puntali
Combina criteri geografici con qualità e completezza dei dati
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.environmental import EnvironmentalData
from datetime import datetime, timedelta

def calculate_data_quality_score(record: EnvironmentalData) -> float:
    """
    Calcola score di qualità per un record ambientale (0-100)
    
    Fattori considerati:
    - Completezza dei parametri
    - Freshness dei dati
    - Affidabilità della fonte
    - Consistenza temporale
    """
    score = 0.0
    
    # 1. Completezza parametri (40 punti max)
    key_parameters = ['pm25', 'pm10', 'no2', 'ozone', 'temperature_avg', 'humidity']
    available_params = sum(1 for param in key_parameters 
                          if getattr(record, param, None) is not None)
    completeness_score = (available_params / len(key_parameters)) * 40
    score += completeness_score
    
    # 2. Freshness dei dati (25 punti max)
    if record.measurement_date:
        days_old = (datetime.now().date() - record.measurement_date).days
        if days_old <= 1:
            freshness_score = 25
        elif days_old <= 7:
            freshness_score = 20
        elif days_old <= 30:
            freshness_score = 15
        elif days_old <= 90:
            freshness_score = 10
        else:
            freshness_score = 5
        score += freshness_score
    
    # 3. Affidabilità fonte (20 punti max)
    source_reliability = {
        'ARPA': 20,
        'ISPRA': 18,
        'ISTAT': 15,
        'Regional': 12,
        'Municipal': 10,
        'Private': 5
    }
    if record.data_source:
        for source, points in source_reliability.items():
            if source.lower() in record.data_source.lower():
                score += points
                break
        else:
            score += 5  # Fonte sconosciuta
    
    # 4. Coordinate precision (10 punti max)
    if record.latitude and record.longitude:
        # Più decimali = maggiore precisione
        lat_precision = len(str(record.latitude).split('.')[-1])
        lon_precision = len(str(record.longitude).split('.')[-1])
        avg_precision = (lat_precision + lon_precision) / 2
        precision_score = min(avg_precision * 2, 10)
        score += precision_score
    
    # 5. Bonus per dati recenti e completi (5 punti max)
    if (record.measurement_date and 
        (datetime.now().date() - record.measurement_date).days <= 7 and
        available_params >= 4):
        score += 5
    
    return min(score, 100.0)

def select_points_by_quality_threshold(
    db: Session,
    geojson_polygon: Dict[str, Any],
    min_quality_score: float = 60.0,
    min_points: int = 10,
    max_points: int = 100
) -> List[EnvironmentalData]:
    """
    Seleziona punti basandosi su soglia di qualità
    
    Args:
        min_quality_score: Score minimo di qualità (0-100)
        min_points: Numero minimo di punti richiesto
        max_points: Numero massimo da restituire
    """
    from .spatial_selection import select_environmental_points_in_polygon
    from .distance_selection import select_points_by_distance
    
    # 1. Prima strategia: punti geometricamente dentro il poligono
    candidate_points = select_environmental_points_in_polygon(db, geojson_polygon)
    
    # 2. Se pochi punti, espandi con buffer zone
    if len(candidate_points) < min_points:
        buffer_points = select_points_by_distance(
            db, geojson_polygon, max_distance_km=20.0
        )
        # Unisci evitando duplicati
        existing_ids = {p.id for p in candidate_points}
        for point in buffer_points:
            if point.id not in existing_ids:
                candidate_points.append(point)
    
    # 3. Calcola quality scores
    points_with_quality = []
    for point in candidate_points:
        quality_score = calculate_data_quality_score(point)
        if quality_score >= min_quality_score:
            points_with_quality.append((point, quality_score))
    
    # 4. Se ancora pochi punti, rilassa la soglia
    if len(points_with_quality) < min_points:
        relaxed_threshold = min_quality_score * 0.7  # Riduce soglia del 30%
        points_with_quality = [
            (point, calculate_data_quality_score(point)) 
            for point in candidate_points
            if calculate_data_quality_score(point) >= relaxed_threshold
        ]
    
    # 5. Ordina per qualità decrescente e limita
    points_with_quality.sort(key=lambda x: x[1], reverse=True)
    selected_points = [point[0] for point in points_with_quality[:max_points]]
    
    return selected_points

def select_points_with_temporal_consistency(
    db: Session,
    geojson_polygon: Dict[str, Any],
    time_window_days: int = 30,
    min_measurements_per_station: int = 5
) -> List[EnvironmentalData]:
    """
    Seleziona punti con consistenza temporale per analisi trend
    
    Utile per analisi che richiedono serie temporali stabili
    """
    from .spatial_selection import select_environmental_points_in_polygon
    
    # Data di riferimento
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=time_window_days)
    
    # Trova stazioni candidate nell'area
    candidate_points = select_environmental_points_in_polygon(db, geojson_polygon)
    
    # Per ogni stazione, conta le misurazioni nel periodo
    station_counts = {}
    for point in candidate_points:
        station_key = (point.latitude, point.longitude, point.istat_code)
        if station_key not in station_counts:
            station_counts[station_key] = []
        station_counts[station_key].append(point)
    
    # Filtra stazioni con abbastanza dati
    consistent_points = []
    for station_key, measurements in station_counts.items():
        # Conta misurazioni nel time window
        recent_measurements = [
            m for m in measurements 
            if m.measurement_date and start_date <= m.measurement_date <= end_date
        ]
        
        if len(recent_measurements) >= min_measurements_per_station:
            # Prendi le misurazioni più recenti da questa stazione
            recent_measurements.sort(key=lambda x: x.measurement_date, reverse=True)
            consistent_points.extend(recent_measurements[:10])  # Max 10 per stazione
    
    return consistent_points

def smart_selection_algorithm(
    db: Session,
    geojson_polygon: Dict[str, Any],
    analysis_type: str = "correlation",  # "correlation", "hotspot", "trend"
    priority_pollutants: List[str] = None
) -> Dict[str, Any]:
    """
    Algoritmo intelligente che adatta la selezione al tipo di analisi
    
    Args:
        analysis_type: Tipo di analisi richiesta
        priority_pollutants: Inquinanti prioritari per l'analisi
    
    Returns:
        Dict con punti selezionati e metadati della selezione
    """
    
    if priority_pollutants is None:
        priority_pollutants = ['pm25', 'pm10', 'no2']
    
    selection_strategy = {
        "correlation": {
            "min_quality": 70.0,
            "temporal_consistency": True,
            "min_points": 15,
            "buffer_km": 10.0
        },
        "hotspot": {
            "min_quality": 60.0,
            "spatial_density": True,
            "min_points": 20,
            "buffer_km": 5.0
        },
        "trend": {
            "min_quality": 80.0,
            "temporal_window_days": 90,
            "min_measurements_per_station": 10,
            "buffer_km": 15.0
        }
    }
    
    config = selection_strategy.get(analysis_type, selection_strategy["correlation"])
    
    if analysis_type == "trend":
        selected_points = select_points_with_temporal_consistency(
            db, geojson_polygon,
            time_window_days=config["temporal_window_days"],
            min_measurements_per_station=config["min_measurements_per_station"]
        )
    else:
        selected_points = select_points_by_quality_threshold(
            db, geojson_polygon,
            min_quality_score=config["min_quality"],
            min_points=config["min_points"]
        )
    
    # Calcola statistiche di selezione
    quality_scores = [calculate_data_quality_score(p) for p in selected_points]
    
    return {
        "selected_points": selected_points,
        "selection_metadata": {
            "total_points": len(selected_points),
            "analysis_type": analysis_type,
            "avg_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "min_quality_score": min(quality_scores) if quality_scores else 0,
            "max_quality_score": max(quality_scores) if quality_scores else 0,
            "data_sources": list(set(p.data_source for p in selected_points if p.data_source)),
            "date_range": {
                "earliest": min(p.measurement_date for p in selected_points if p.measurement_date),
                "latest": max(p.measurement_date for p in selected_points if p.measurement_date)
            } if selected_points else None,
            "geographic_coverage": {
                "municipalities": len(set(p.istat_code for p in selected_points)),
                "bbox": _calculate_bbox(selected_points) if selected_points else None
            }
        }
    }

def _calculate_bbox(points: List[EnvironmentalData]) -> Dict[str, float]:
    """Helper per calcolare bounding box dei punti selezionati"""
    valid_points = [(p.longitude, p.latitude) for p in points 
                   if p.longitude is not None and p.latitude is not None]
    
    if not valid_points:
        return {}
    
    lons, lats = zip(*valid_points)
    return {
        "min_lon": min(lons),
        "max_lon": max(lons),
        "min_lat": min(lats),
        "max_lat": max(lats)
    }

# Esempio di utilizzo ottimale
def recommend_selection_strategy():
    """
    Raccomandazioni per la selezione dei dati puntali nel tuo poligono
    """
    recommendations = {
        "per_analisi_correlazione": {
            "strategia": "smart_selection_algorithm con analysis_type='correlation'",
            "motivo": "Serve consistenza temporale e qualità alta",
            "parametri": "min_quality=70, temporal_consistency=True"
        },
        "per_hotspot_analysis": {
            "strategia": "point_in_polygon + buffer_zone se necessario", 
            "motivo": "Serve densità spaziale alta nell'area specifica",
            "parametri": "geometric containment + 5km buffer"
        },
        "per_trend_analysis": {
            "strategia": "select_points_with_temporal_consistency",
            "motivo": "Serve storico dati lungo e stazioni stabili",
            "parametri": "time_window=90 giorni, min_measurements=10"
        },
        "fallback_generale": {
            "strategia": "hybrid_selection_strategy", 
            "motivo": "Combina più approcci con priorità",
            "parametri": "priority=['geometric', 'administrative', 'distance']"
        }
    }
    
    return recommendations
