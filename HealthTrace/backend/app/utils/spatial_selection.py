"""
Implementazione Point-in-Polygon per HealthTrace
Come decidere quali dati puntali selezionare per un poligono GeoJSON
"""

from typing import List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from app.models.environmental import EnvironmentalData
import math

def point_in_polygon(point: Tuple[float, float], polygon: List[List[float]]) -> bool:
    """
    Ray-casting algorithm per verificare se un punto è dentro un poligono
    
    Args:
        point: (longitude, latitude) del punto ambientale
        polygon: Lista di coordinate [longitude, latitude] del poligono GeoJSON
    
    Returns:
        True se il punto è dentro il poligono
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside


def select_environmental_points_in_polygon(
    db: Session, 
    geojson_polygon: Dict[str, Any],
    filters: Dict[str, Any] = None
) -> List[EnvironmentalData]:
    """
    Seleziona tutti i punti ambientali che cadono dentro un poligono GeoJSON
    
    Args:
        db: Database session
        geojson_polygon: GeoJSON polygon come nel tuo esempio
        filters: Filtri aggiuntivi (date, inquinanti, etc.)
    
    Returns:
        Lista di record EnvironmentalData dentro il poligono
    """
    # Estrai le coordinate del poligono
    if geojson_polygon["type"] != "Polygon":
        raise ValueError("Solo poligoni supportati")
    
    polygon_coords = geojson_polygon["coordinates"][0]  # Primo anello (outline)
    
    # Query base per tutti i punti con coordinate valide
    query = db.query(EnvironmentalData).filter(
        EnvironmentalData.latitude.isnot(None),
        EnvironmentalData.longitude.isnot(None)
    )
    
    # Applica filtri aggiuntivi
    if filters:
        if "start_date" in filters:
            query = query.filter(EnvironmentalData.measurement_date >= filters["start_date"])
        if "end_date" in filters:
            query = query.filter(EnvironmentalData.measurement_date <= filters["end_date"])
        if "istat_code" in filters:
            query = query.filter(EnvironmentalData.istat_code.like(f"{filters['istat_code']}%"))
        if "pollutant" in filters and "min_value" in filters:
            pollutant_col = getattr(EnvironmentalData, filters["pollutant"], None)
            if pollutant_col:
                query = query.filter(pollutant_col >= filters["min_value"])
    
    # Ottieni tutti i record candidati
    all_points = query.all()
    
    # Filtra geometricamente
    selected_points = []
    for record in all_points:
        point = (record.longitude, record.latitude)
        if point_in_polygon(point, polygon_coords):
            selected_points.append(record)
    
    return selected_points


def get_bounding_box_filter(polygon_coords: List[List[float]]) -> Dict[str, float]:
    """
    Calcola bounding box per pre-filtrare i punti (ottimizzazione)
    """
    lons = [coord[0] for coord in polygon_coords]
    lats = [coord[1] for coord in polygon_coords]
    
    return {
        "min_lon": min(lons),
        "max_lon": max(lons), 
        "min_lat": min(lats),
        "max_lat": max(lats)
    }


# Esempio di utilizzo con il tuo poligono
def example_usage():
    # Il tuo poligono GeoJSON
    napoli_area = {
        "type": "Polygon", 
        "coordinates": [
            [
                [14.25, 40.85],  # [longitude, latitude]
                [14.30, 40.85],
                [14.30, 40.90],
                [14.25, 40.90],
                [14.25, 40.85]   # Chiude il poligono
            ]
        ]
    }
    
    # Filtri aggiuntivi per la selezione
    selection_filters = {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "pollutant": "pm25",
        "min_value": 10.0  # Solo PM2.5 > 10 μg/m³
    }
    
    # Seleziona i punti
    # selected_points = select_environmental_points_in_polygon(
    #     db, napoli_area, selection_filters
    # )
    
    return f"Strategia: seleziona punti geograficamente contenuti nel poligono"
