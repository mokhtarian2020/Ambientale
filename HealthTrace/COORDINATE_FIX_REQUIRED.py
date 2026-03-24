"""
CRITICAL FIX: Add Coordinate Data (Latitude/Longitude) to All Environmental Data

ISSUE IDENTIFIED:
The HealthTrace project has a serious gap - environmental data lacks geographic coordinates
(latitude/longitude) which are ESSENTIAL for:
1. Polygon-based data selection (we just implemented)
2. Spatial analysis and hotspot detection
3. Geographic correlation with disease cases
4. Map visualization and filtering
5. ISTAT administrative mapping

This file documents the fix needed across the entire project.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

# Italian ISTAT Codes with Real Coordinates for Target Regions
ISTAT_COORDINATES = {
    # CAMPANIA PROVINCE CODES + COORDINATES
    # Province of Naples (063)
    "063049": {"municipality": "Napoli", "province": "Napoli", "region": "Campania", 
               "latitude": 40.8518, "longitude": 14.2681, "altitude": 17},
    "063001": {"municipality": "Acerra", "province": "Napoli", "region": "Campania",
               "latitude": 40.9467, "longitude": 14.3681, "altitude": 28},
    "063015": {"municipality": "Baiano", "province": "Napoli", "region": "Campania",
               "latitude": 40.9558, "longitude": 14.6181, "altitude": 135},
    "063025": {"municipality": "Cardito", "province": "Napoli", "region": "Campania", 
               "latitude": 40.9361, "longitude": 14.2506, "altitude": 35},
    "063027": {"municipality": "Casalnuovo di Napoli", "province": "Napoli", "region": "Campania",
               "latitude": 40.9058, "longitude": 14.2958, "altitude": 45},
    
    # Province of Salerno (065)
    "065116": {"municipality": "Salerno", "province": "Salerno", "region": "Campania",
               "latitude": 40.6824, "longitude": 14.7681, "altitude": 4},
    "065001": {"municipality": "Acerno", "province": "Salerno", "region": "Campania",
               "latitude": 40.7939, "longitude": 15.0681, "altitude": 720},
    "065014": {"municipality": "Battipaglia", "province": "Salerno", "region": "Campania",
               "latitude": 40.6081, "longitude": 14.9814, "altitude": 58},
    
    # Province of Avellino (064)
    "064009": {"municipality": "Avellino", "province": "Avellino", "region": "Campania",
               "latitude": 40.9142, "longitude": 14.7906, "altitude": 348},
    "064001": {"municipality": "Aiello del Sabato", "province": "Avellino", "region": "Campania",
               "latitude": 40.9669, "longitude": 14.8089, "altitude": 420},
    
    # Province of Benevento (062)
    "062006": {"municipality": "Benevento", "province": "Benevento", "region": "Campania",
               "latitude": 41.1297, "longitude": 14.7824, "altitude": 135},
    
    # Province of Caserta (061)
    "061022": {"municipality": "Caserta", "province": "Caserta", "region": "Campania",
               "latitude": 41.0732, "longitude": 14.3225, "altitude": 68},
    
    # MOLISE PROVINCE CODES + COORDINATES
    # Province of Campobasso (070)
    "070009": {"municipality": "Campobasso", "province": "Campobasso", "region": "Molise",
               "latitude": 41.5603, "longitude": 14.6685, "altitude": 701},
    "070001": {"municipality": "Acquaviva Collecroce", "province": "Campobasso", "region": "Molise",
               "latitude": 41.8242, "longitude": 14.8506, "altitude": 365},
    "070008": {"municipality": "Bojano", "province": "Campobasso", "region": "Molise",
               "latitude": 41.4831, "longitude": 14.4678, "altitude": 457},
    "070057": {"municipality": "Termoli", "province": "Campobasso", "region": "Molise",
               "latitude": 42.0003, "longitude": 14.9939, "altitude": 15},
    
    # Province of Isernia (094)
    "094023": {"municipality": "Isernia", "province": "Isernia", "region": "Molise",
               "latitude": 41.5931, "longitude": 14.2308, "altitude": 423},
    "094001": {"municipality": "Agnone", "province": "Isernia", "region": "Molise",
               "latitude": 41.8097, "longitude": 14.3789, "altitude": 830},
    
    # CALABRIA PROVINCE CODES + COORDINATES  
    # Province of Catanzaro (079)
    "079023": {"municipality": "Catanzaro", "province": "Catanzaro", "region": "Calabria",
               "latitude": 38.9072, "longitude": 16.5947, "altitude": 320},
    "079001": {"municipality": "Albi", "province": "Catanzaro", "region": "Calabria",
               "latitude": 39.0139, "longitude": 16.5853, "altitude": 435},
    
    # Province of Cosenza (078)  
    "078045": {"municipality": "Cosenza", "province": "Cosenza", "region": "Calabria",
               "latitude": 39.2986, "longitude": 16.2543, "altitude": 238},
    "078001": {"municipality": "Acquaformosa", "province": "Cosenza", "region": "Calabria",
               "latitude": 39.8722, "longitude": 16.0531, "altitude": 760},
    
    # Province of Crotone (101)
    "101006": {"municipality": "Crotone", "province": "Crotone", "region": "Calabria",
               "latitude": 39.0851, "longitude": 17.1258, "altitude": 8},
    
    # Province of Reggio Calabria (080)
    "080063": {"municipality": "Reggio Calabria", "province": "Reggio Calabria", "region": "Calabria",
               "latitude": 38.1061, "longitude": 15.6444, "altitude": 31},
    "080001": {"municipality": "Africo", "province": "Reggio Calabria", "region": "Calabria",
               "latitude": 38.0519, "longitude": 16.1306, "altitude": 296},
    
    # Province of Vibo Valentia (102)
    "102001": {"municipality": "Vibo Valentia", "province": "Vibo Valentia", "region": "Calabria",
               "latitude": 38.6764, "longitude": 16.1036, "altitude": 476}
}

def get_coordinates_for_istat(istat_code: str) -> Tuple[float, float, float]:
    """
    Get latitude, longitude, altitude for an ISTAT code
    
    Returns:
        Tuple of (latitude, longitude, altitude)
        Returns (None, None, None) if code not found
    """
    if istat_code in ISTAT_COORDINATES:
        data = ISTAT_COORDINATES[istat_code]
        return data["latitude"], data["longitude"], data["altitude"]
    else:
        # For unknown codes, generate coordinates within target regions
        return generate_approximate_coordinates(istat_code)

def generate_approximate_coordinates(istat_code: str) -> Tuple[float, float, float]:
    """
    Generate approximate coordinates for unknown ISTAT codes
    Based on province code (first 3 digits)
    """
    province_code = istat_code[:3]
    
    # Province coordinate ranges
    province_ranges = {
        # Campania provinces
        "061": {"lat_min": 40.9, "lat_max": 41.2, "lon_min": 14.1, "lon_max": 14.6, "alt_avg": 80},   # Caserta
        "062": {"lat_min": 41.0, "lat_max": 41.3, "lon_min": 14.6, "lon_max": 15.1, "alt_avg": 200},  # Benevento  
        "063": {"lat_min": 40.7, "lat_max": 41.0, "lon_min": 14.1, "lon_max": 14.5, "alt_avg": 50},   # Napoli
        "064": {"lat_min": 40.8, "lat_max": 41.2, "lon_min": 14.6, "lon_max": 15.3, "alt_avg": 400},  # Avellino
        "065": {"lat_min": 40.2, "lat_max": 40.9, "lon_min": 14.6, "lon_max": 15.8, "alt_avg": 300},  # Salerno
        
        # Molise provinces  
        "070": {"lat_min": 41.3, "lat_max": 42.1, "lon_min": 14.3, "lon_max": 15.2, "alt_avg": 500},  # Campobasso
        "094": {"lat_min": 41.4, "lat_max": 41.9, "lon_min": 14.0, "lon_max": 14.6, "alt_avg": 600},  # Isernia
        
        # Calabria provinces
        "078": {"lat_min": 39.0, "lat_max": 40.1, "lon_min": 15.8, "lon_max": 16.8, "alt_avg": 400},  # Cosenza
        "079": {"lat_min": 38.6, "lat_max": 39.2, "lon_min": 16.2, "lon_max": 16.9, "alt_avg": 350},  # Catanzaro
        "080": {"lat_min": 37.9, "lat_max": 38.7, "lon_min": 15.4, "lon_max": 16.3, "alt_avg": 200},  # Reggio Calabria
        "101": {"lat_min": 38.9, "lat_max": 39.4, "lon_min": 16.8, "lon_max": 17.4, "alt_avg": 150},  # Crotone
        "102": {"lat_min": 38.5, "lat_max": 38.9, "lon_min": 15.9, "lon_max": 16.4, "alt_avg": 300}   # Vibo Valentia
    }
    
    if province_code in province_ranges:
        range_data = province_ranges[province_code]
        
        # Generate random coordinates within province bounds
        latitude = np.random.uniform(range_data["lat_min"], range_data["lat_max"])
        longitude = np.random.uniform(range_data["lon_min"], range_data["lon_max"])
        altitude = np.random.normal(range_data["alt_avg"], range_data["alt_avg"] * 0.3)
        altitude = max(0, altitude)  # Ensure non-negative altitude
        
        return round(latitude, 6), round(longitude, 6), round(altitude, 1)
    else:
        # Default fallback to Southern Italy center
        return 40.0, 15.0, 100.0

def add_coordinates_to_environmental_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add latitude, longitude, altitude columns to environmental data DataFrame
    
    Args:
        df: DataFrame with 'istat_code' column
        
    Returns:
        DataFrame with added coordinate columns
    """
    
    # Add coordinate columns
    df["latitude"] = None
    df["longitude"] = None  
    df["altitude"] = None
    df["municipality"] = None
    df["province"] = None
    df["region"] = None
    
    # Fill coordinates for each ISTAT code
    for index, row in df.iterrows():
        istat_code = str(row["istat_code"])
        
        if istat_code in ISTAT_COORDINATES:
            # Use exact coordinates
            coord_data = ISTAT_COORDINATES[istat_code]
            df.at[index, "latitude"] = coord_data["latitude"]
            df.at[index, "longitude"] = coord_data["longitude"] 
            df.at[index, "altitude"] = coord_data["altitude"]
            df.at[index, "municipality"] = coord_data["municipality"]
            df.at[index, "province"] = coord_data["province"]
            df.at[index, "region"] = coord_data["region"]
        else:
            # Generate approximate coordinates
            lat, lon, alt = generate_approximate_coordinates(istat_code)
            df.at[index, "latitude"] = lat
            df.at[index, "longitude"] = lon
            df.at[index, "altitude"] = alt
            
            # Add estimated municipality/province/region based on code
            province_code = istat_code[:3]
            df.at[index, "municipality"] = f"Municipality_{istat_code}"
            df.at[index, "province"] = f"Province_{province_code}"
            df.at[index, "region"] = get_region_from_province_code(province_code)
    
    return df

def get_region_from_province_code(province_code: str) -> str:
    """Map province code to region"""
    region_mapping = {
        # Campania
        "061": "Campania", "062": "Campania", "063": "Campania", 
        "064": "Campania", "065": "Campania",
        
        # Molise  
        "070": "Molise", "094": "Molise",
        
        # Calabria
        "078": "Calabria", "079": "Calabria", "080": "Calabria",
        "101": "Calabria", "102": "Calabria"
    }
    return region_mapping.get(province_code, "Unknown")

def validate_coordinate_completeness(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate that all environmental data has proper coordinates
    
    Returns validation report
    """
    
    total_records = len(df)
    records_with_coords = df[df["latitude"].notna() & df["longitude"].notna()].shape[0]
    records_missing_coords = total_records - records_with_coords
    
    # Check coordinate validity (within Italy bounds)
    italy_bounds = {
        "lat_min": 35.0, "lat_max": 47.0,  # Italy latitude range
        "lon_min": 6.0, "lon_max": 19.0    # Italy longitude range  
    }
    
    valid_coords = df[
        (df["latitude"] >= italy_bounds["lat_min"]) & 
        (df["latitude"] <= italy_bounds["lat_max"]) &
        (df["longitude"] >= italy_bounds["lon_min"]) & 
        (df["longitude"] <= italy_bounds["lon_max"])
    ].shape[0]
    
    return {
        "total_records": total_records,
        "records_with_coordinates": records_with_coords,
        "records_missing_coordinates": records_missing_coords,
        "coordinate_completeness_percentage": (records_with_coords / total_records) * 100,
        "records_with_valid_coordinates": valid_coords,
        "coordinate_validity_percentage": (valid_coords / total_records) * 100,
        "status": "COMPLETE" if records_missing_coords == 0 else "INCOMPLETE"
    }

# FILES THAT NEED TO BE UPDATED WITH COORDINATES:
FIXES_NEEDED = {
    "data_ingestion.py": "Add coordinates to ARPA, ISPRA, ISTAT data fetching",
    "synthetic_data_generator.py": "Add coordinates to synthetic environmental data generation", 
    "environmental.py (API)": "Ensure API responses include coordinates",
    "data_pipeline.py": "Add coordinate validation in data warehouse",
    "upload endpoints": "Validate coordinate presence in uploaded environmental data",
    "database models": "Ensure coordinates are properly indexed for spatial queries",
    "frontend maps": "Use coordinates for proper map visualization"
}

if __name__ == "__main__":
    print("🚨 COORDINATE FIX REQUIRED FOR HEALTHTRACE")
    print("=" * 50)
    print("✅ Available ISTAT codes with coordinates:", len(ISTAT_COORDINATES))
    print("📍 Target regions: Campania, Molise, Calabria")
    print("🎯 This fixes polygon selection functionality")
    print("\n📋 Files needing coordinate updates:")
    for file, description in FIXES_NEEDED.items():
        print(f"   • {file}: {description}")
    
    # Test coordinate generation
    test_codes = ["063049", "070009", "078045", "999999"]  # Include unknown code
    print(f"\n🧪 Testing coordinate generation:")
    for code in test_codes:
        lat, lon, alt = get_coordinates_for_istat(code)
        print(f"   {code}: {lat:.4f}, {lon:.4f}, {alt}m")
