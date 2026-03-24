"""
Strategia Distance-Based per selezione dati puntali
Alternativa quando hai poche stazioni di monitoraggio sparse
"""

from typing import List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from app.models.environmental import EnvironmentalData
import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcola distanza in km tra due punti usando formula di Haversine
    """
    R = 6371  # Raggio Terra in km
    
    # Converti gradi in radianti
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Formula di Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def polygon_centroid(polygon_coords: List[List[float]]) -> Tuple[float, float]:
    """
    Calcola il centroide di un poligono
    """
    n = len(polygon_coords)
    if n == 0:
        return 0.0, 0.0
    
    sum_lon = sum(coord[0] for coord in polygon_coords)
    sum_lat = sum(coord[1] for coord in polygon_coords)
    
    return sum_lon / n, sum_lat / n

def select_points_by_distance(
    db: Session,
    geojson_polygon: Dict[str, Any], 
    max_distance_km: float = 10.0,
    max_points: int = 50
) -> List[EnvironmentalData]:
    """
    Seleziona punti ambientali entro una certa distanza dal centroide del poligono
    
    Strategia utile quando:
    - Hai poche stazioni di monitoraggio
    - Vuoi includere stazioni vicine anche se fuori dal poligono
    - Hai bisogno di un numero minimo di punti per l'analisi
    
    Args:
        db: Database session
        geojson_polygon: Il tuo poligono GeoJSON
        max_distance_km: Distanza massima dal centroide (default 10km)
        max_points: Numero massimo di punti da restituire
    
    Returns:
        Lista ordinata per distanza crescente
    """
    polygon_coords = geojson_polygon["coordinates"][0]
    centroid_lon, centroid_lat = polygon_centroid(polygon_coords)
    
    # Query tutti i punti con coordinate
    all_points = db.query(EnvironmentalData).filter(
        EnvironmentalData.latitude.isnot(None),
        EnvironmentalData.longitude.isnot(None)
    ).all()
    
    # Calcola distanze e ordina
    points_with_distance = []
    for record in all_points:
        distance = haversine_distance(
            centroid_lat, centroid_lon,
            record.latitude, record.longitude
        )
        if distance <= max_distance_km:
            points_with_distance.append((record, distance))
    
    # Ordina per distanza crescente e limita il numero
    points_with_distance.sort(key=lambda x: x[1])
    selected_points = [point[0] for point in points_with_distance[:max_points]]
    
    return selected_points

def select_points_by_buffer_zone(
    db: Session,
    geojson_polygon: Dict[str, Any],
    buffer_km: float = 5.0
) -> List[EnvironmentalData]:
    """
    Seleziona punti dentro il poligono + zona buffer attorno
    
    Strategia ibrida: geometria + distanza
    """
    from .spatial_selection import point_in_polygon, select_environmental_points_in_polygon
    
    # 1. Prima prendi punti dentro il poligono
    points_inside = select_environmental_points_in_polygon(db, geojson_polygon)
    
    # 2. Poi aggiungi punti nella zona buffer
    points_in_buffer = select_points_by_distance(
        db, geojson_polygon, max_distance_km=buffer_km
    )
    
    # 3. Unisci senza duplicati
    all_ids = set()
    combined_points = []
    
    # Priorità ai punti dentro il poligono
    for point in points_inside:
        if point.id not in all_ids:
            combined_points.append(point)
            all_ids.add(point.id)
    
    # Aggiungi punti buffer che non sono già inclusi
    for point in points_in_buffer:
        if point.id not in all_ids:
            combined_points.append(point)
            all_ids.add(point.id)
    
    return combined_points

# Esempio pratico per il tuo caso
def example_napoli_selection():
    napoli_area = {
        "type": "Polygon", 
        "coordinates": [
            [
                [14.25, 40.85],
                [14.30, 40.85], 
                [14.30, 40.90],
                [14.25, 40.90],
                [14.25, 40.85]
            ]
        ]
    }
    
    strategies = {
        "strict_geometric": "Solo punti esattamente dentro il poligono",
        "distance_10km": "Punti entro 10km dal centroide", 
        "buffer_5km": "Punti dentro + buffer zone 5km",
        "nearest_20_stations": "Le 20 stazioni più vicine indipendentemente dalla distanza"
    }
    
    return strategies
