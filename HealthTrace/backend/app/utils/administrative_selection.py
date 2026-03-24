"""
Strategia Administrative-Based per selezione dati puntali
Usa i codici ISTAT per identificare quali comuni/province sono nel poligono
"""

from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session
from app.models.environmental import EnvironmentalData

# Mappatura ISTAT per le regioni target di HealthTrace
CAMPANIA_MUNICIPALITIES = {
    # Provincia di Napoli (063)
    "063049": {"name": "Napoli", "lat": 40.8518, "lon": 14.2681},
    "063001": {"name": "Acerra", "lat": 40.9467, "lon": 14.3681},
    "063004": {"name": "Afragola", "lat": 40.9244, "lon": 14.3039},
    "063008": {"name": "Arzano", "lat": 40.9153, "lon": 14.2731},
    "063015": {"name": "Baiano", "lat": 40.9558, "lon": 14.6181},
    "063019": {"name": "Brusciano", "lat": 40.9231, "lon": 14.4522},
    "063021": {"name": "Calvanico", "lat": 40.7622, "lon": 14.7361},
    "063025": {"name": "Cardito", "lat": 40.9361, "lon": 14.2506},
    "063027": {"name": "Casalnuovo di Napoli", "lat": 40.9058, "lon": 14.2958},
    "063028": {"name": "Casamarciano", "lat": 40.9219, "lon": 14.4458},
    # ... altri comuni (tronco per brevità)
    
    # Provincia di Salerno (065) 
    "065116": {"name": "Salerno", "lat": 40.6824, "lon": 14.7681},
    "065001": {"name": "Acerno", "lat": 40.7939, "lon": 15.0681},
    # ... altri comuni
    
    # Provincia di Avellino (064)
    "064009": {"name": "Avellino", "lat": 40.9142, "lon": 14.7906},
    # ... altri comuni
}

def get_municipalities_in_polygon(
    geojson_polygon: Dict[str, Any],
    istat_mapping: Dict[str, Dict] = CAMPANIA_MUNICIPALITIES
) -> Set[str]:
    """
    Identifica quali comuni ISTAT hanno il centroide dentro il poligono
    
    Args:
        geojson_polygon: Il tuo poligono GeoJSON
        istat_mapping: Mappatura codice ISTAT -> coordinate centroide
    
    Returns:
        Set di codici ISTAT dei comuni interessati
    """
    from .spatial_selection import point_in_polygon
    
    polygon_coords = geojson_polygon["coordinates"][0]
    selected_istat_codes = set()
    
    for istat_code, info in istat_mapping.items():
        municipality_point = (info["lon"], info["lat"])
        if point_in_polygon(municipality_point, polygon_coords):
            selected_istat_codes.add(istat_code)
    
    return selected_istat_codes

def select_points_by_istat_codes(
    db: Session,
    istat_codes: Set[str],
    filters: Dict[str, Any] = None
) -> List[EnvironmentalData]:
    """
    Seleziona tutti i punti ambientali dai comuni ISTAT specificati
    
    Strategia utile quando:
    - Hai buona copertura di stazioni per comune
    - Vuoi allinearti con i confini amministrativi
    - Hai bisogno di correlazione con dati sanitari per comune
    """
    query = db.query(EnvironmentalData).filter(
        EnvironmentalData.istat_code.in_(istat_codes)
    )
    
    # Applica filtri aggiuntivi
    if filters:
        if "start_date" in filters:
            query = query.filter(EnvironmentalData.measurement_date >= filters["start_date"])
        if "end_date" in filters:
            query = query.filter(EnvironmentalData.measurement_date <= filters["end_date"])
        if "min_pm25" in filters:
            query = query.filter(EnvironmentalData.pm25 >= filters["min_pm25"])
    
    return query.all()

def select_points_by_administrative_hierarchy(
    db: Session,
    geojson_polygon: Dict[str, Any],
    level: str = "municipality"  # "municipality", "province", "region"
) -> List[EnvironmentalData]:
    """
    Selezione gerarchica basata su livello amministrativo
    
    Args:
        level: Livello di aggregazione
            - "municipality": Comuni specifici nel poligono
            - "province": Province che intersecano il poligono  
            - "region": Regione intera se poligono la tocca
    """
    
    if level == "municipality":
        # Trova comuni nel poligono
        selected_istat = get_municipalities_in_polygon(geojson_polygon)
        return select_points_by_istat_codes(db, selected_istat)
        
    elif level == "province":
        # Trova province intersecate
        selected_istat = get_municipalities_in_polygon(geojson_polygon)
        # Estrai codici provincia (prime 3 cifre)
        province_codes = set()
        for istat_code in selected_istat:
            province_code = istat_code[:3]  # Es: "063" da "063049"
            province_codes.add(province_code)
        
        # Prendi tutti i comuni di quelle province
        query = db.query(EnvironmentalData)
        for province_code in province_codes:
            query = query.filter(EnvironmentalData.istat_code.like(f"{province_code}%"))
        return query.all()
        
    elif level == "region":
        # Se il poligono tocca la Campania, prendi tutta la Campania
        selected_istat = get_municipalities_in_polygon(geojson_polygon)
        if selected_istat:  # Se interseca almeno un comune campano
            return db.query(EnvironmentalData).filter(
                EnvironmentalData.region == "Campania"
            ).all()
    
    return []

def hybrid_selection_strategy(
    db: Session,
    geojson_polygon: Dict[str, Any],
    strategy_priority: List[str] = ["geometric", "administrative", "distance"]
) -> List[EnvironmentalData]:
    """
    Strategia ibrida che combina multiple approcci in ordine di priorità
    
    Args:
        strategy_priority: Ordine di applicazione delle strategie
    
    Returns:
        Punti selezionati con l'approccio più adatto
    """
    from .spatial_selection import select_environmental_points_in_polygon
    from .distance_selection import select_points_by_distance
    
    results = []
    
    for strategy in strategy_priority:
        if strategy == "geometric":
            points = select_environmental_points_in_polygon(db, geojson_polygon)
            if len(points) >= 10:  # Soglia minima
                return points
            results.extend(points)
            
        elif strategy == "administrative":
            selected_istat = get_municipalities_in_polygon(geojson_polygon)
            points = select_points_by_istat_codes(db, selected_istat)
            if len(points) >= 5:
                return points
            results.extend(points)
            
        elif strategy == "distance":
            points = select_points_by_distance(db, geojson_polygon, max_distance_km=15.0)
            results.extend(points)
            return results  # Fallback finale
    
    # Rimuovi duplicati
    unique_points = []
    seen_ids = set()
    for point in results:
        if point.id not in seen_ids:
            unique_points.append(point)
            seen_ids.add(point.id)
    
    return unique_points

# Esempio per il tuo poligono di Napoli
def example_istat_selection():
    napoli_area = {
        "type": "Polygon", 
        "coordinates": [
            [
                [14.25, 40.85],  # Copre parte del centro di Napoli
                [14.30, 40.85],
                [14.30, 40.90], 
                [14.25, 40.90],
                [14.25, 40.85]
            ]
        ]
    }
    
    # Comuni che probabilmente intersecano quest'area:
    likely_municipalities = [
        "063049",  # Napoli centro
        "063082",  # San Giorgio a Cremano  
        "063025",  # Cardito
        # Basato sulle coordinate del poligono
    ]
    
    return {
        "polygon_covers": "Centro Napoli + comuni limitrofi",
        "istat_strategy": "Usa codici ISTAT per selezione amministrativa",
        "benefit": "Allineamento con dati sanitari e confini ufficiali"
    }
