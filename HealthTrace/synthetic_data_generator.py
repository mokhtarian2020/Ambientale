"""
Synthetic Data Generator for HealthTrace Platform
Creates realistic environmental and health data for testing the 3-disease platform:
- Influenza (Respiratory)
- Legionellosis (Water-Aerosol)
- Hepatitis A (Foodborne/Waterborne)

Based on Italian environmental health patterns and real ARPA/ISPRA data characteristics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import json
import random
from typing import Dict, List, Any
import os
from pathlib import Path

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)

#!/usr/bin/env python3
"""
Synthetic Data Generator for HealthTrace Platform
Generates realistic Italian environmental health data for testing all models
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import random

class SyntheticDataGenerator:
    """Generate realistic synthetic data for Italian health monitoring"""
    
    def __init__(self, output_dir: str = "synthetic_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Italian ISTAT codes for target regions
        self.istat_codes = {
            "molise": ["094001", "094002", "094003", "094004", "094005"],  # Molise communes
            "campania": ["081001", "081063", "081055", "081049", "081030"],  # Campania (Naples area)
            "calabria": ["078001", "078005", "078010", "078015", "078020"]   # Calabria communes
        }
        
        # Date range for synthetic data (2 years)
        self.start_date = datetime(2023, 1, 1)
        self.end_date = datetime(2024, 12, 31)
        self.date_range = pd.date_range(self.start_date, self.end_date, freq='D')
        
        # Environmental parameters based on ARPA Campania specifications
        self.pollutants = ["PM10", "PM25", "O3", "NO2", "SO2", "C6H6", "CO"]
        self.climate_params = ["temperature", "humidity", "precipitation", "wind_speed", "pressure"]
        self.water_params = ["ph", "ecoli_count", "residual_chlorine", "water_temperature"]

        
    def generate_environmental_data(self) -> pd.DataFrame:
        """Generate synthetic environmental data matching ARPA Campania format"""
        
        data = []
        
        for date_val in self.date_range:
            for istat_code in self.all_istat_codes:
                
                # Seasonal patterns for realism
                day_of_year = date_val.timetuple().tm_yday
                seasonal_factor = np.sin(2 * np.pi * day_of_year / 365.25)
                
                # Generate air quality data
                for pollutant in self.pollutants:
                    if pollutant == "PM10":
                        # Higher in winter, lower in summer
                        base_value = 30 + 15 * (-seasonal_factor) + np.random.normal(0, 8)
                        value = max(5, base_value)  # Minimum 5 μg/m³
                    elif pollutant == "PM25":
                        # Correlated with PM10 but lower
                        pm10_base = 30 + 15 * (-seasonal_factor)
                        value = max(3, pm10_base * 0.6 + np.random.normal(0, 5))
                    elif pollutant == "O3":
                        # Higher in summer
                        base_value = 80 + 40 * seasonal_factor + np.random.normal(0, 20)
                        value = max(10, base_value)
                    elif pollutant == "NO2":
                        # Higher in winter (heating), urban areas
                        base_value = 25 + 10 * (-seasonal_factor) + np.random.normal(0, 8)
                        value = max(5, base_value)
                    elif pollutant == "SO2":
                        # Generally low in Italy
                        value = max(1, np.random.normal(8, 3))
                    elif pollutant == "C6H6":
                        # Benzene - traffic related
                        value = max(0.5, np.random.normal(2.5, 1))
                    else:  # CO
                        value = max(0.1, np.random.normal(1.2, 0.5))
                    
                    data.append({
                        'date': date_val.date(),
                        'datetime': date_val,
                        'istat_code': istat_code,
                        'parameter': pollutant,
                        'value': round(value, 2),
                        'unit': 'μg/m³' if pollutant != 'CO' else 'mg/m³',
                        'data_source': 'ARPA_CAMPANIA_SYNTHETIC',
                        'station_id': f"STAT_{istat_code}_{pollutant}",
                        'validation_status': 'validated'
                    })
                
                # Generate climate data
                for param in self.climate_params:
                    if param == "temperature":
                        # Seasonal temperature pattern
                        base_temp = 15 + 12 * seasonal_factor + np.random.normal(0, 3)
                        value = base_temp
                        unit = "°C"
                    elif param == "humidity":
                        # Higher humidity in winter
                        base_humidity = 65 + 15 * (-seasonal_factor) + np.random.normal(0, 10)
                        value = max(30, min(95, base_humidity))
                        unit = "%"
                    elif param == "precipitation":
                        # More rain in autumn/winter
                        rain_prob = 0.3 + 0.2 * (-seasonal_factor)
                        if np.random.random() < rain_prob:
                            value = np.random.exponential(8)  # Exponential distribution for rain
                        else:
                            value = 0
                        unit = "mm"
                    elif param == "wind_speed":
                        value = max(0, np.random.normal(3.5, 2))
                        unit = "m/s"
                    else:  # pressure
                        value = np.random.normal(1013, 10)
                        unit = "hPa"
                    
                    data.append({
                        'date': date_val.date(),
                        'datetime': date_val,
                        'istat_code': istat_code,
                        'parameter': param,
                        'value': round(value, 2),
                        'unit': unit,
                        'data_source': 'ISTAT_SYNTHETIC',
                        'station_id': f"METEO_{istat_code}",
                        'validation_status': 'validated'
                    })
                
                # Generate water quality data (weekly sampling)
                if date_val.weekday() == 0:  # Monday sampling
                    for param in self.water_params:
                        if param == "ph":
                            value = np.random.normal(7.2, 0.3)
                            value = max(6.5, min(8.5, value))
                            unit = "pH units"
                        elif param == "ecoli_count":
                            # Log-normal distribution for bacteria
                            value = np.random.lognormal(1, 1.5)
                            unit = "CFU/100ml"
                        elif param == "residual_chlorine":
                            value = max(0.1, np.random.normal(0.5, 0.2))
                            unit = "mg/L"
                        else:  # water_temperature
                            # Water temperature follows air temperature with lag
                            base_temp = 12 + 8 * seasonal_factor + np.random.normal(0, 2)
                            value = base_temp
                            unit = "°C"
                        
                        data.append({
                            'date': date_val.date(),
                            'datetime': date_val,
                            'istat_code': istat_code,
                            'parameter': param,
                            'value': round(value, 2),
                            'unit': unit,
                            'data_source': 'ARPA_CAMPANIA_WATER_SYNTHETIC',
                            'station_id': f"WATER_{istat_code}",
                            'validation_status': 'validated'
                        })
        
        return pd.DataFrame(data)
    
    def generate_disease_cases(self, environmental_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Generate synthetic disease cases correlated with environmental factors"""
        
        # Get daily environmental summaries by ISTAT code
        env_daily = environmental_df.groupby(['date', 'istat_code', 'parameter'])['value'].mean().unstack('parameter').reset_index()
        
        disease_data = {
            'influenza': [],
            'legionellosis': [],
            'hepatitis_a': []
        }
        
        for _, row in env_daily.iterrows():
            date_val = row['date']
            istat_code = row['istat_code']
            
            # Population estimates for ISTAT codes (synthetic)
            population = np.random.randint(10000, 100000)
            
            # INFLUENZA CASES (Respiratory - air quality correlation)
            pm25 = row.get('PM25', 20)
            pm10 = row.get('PM10', 30)
            temp = row.get('temperature', 15)
            humidity = row.get('humidity', 65)
            
            # Influenza model: higher PM2.5, lower temperature = more cases
            flu_risk = (
                0.02 * pm25 +  # PM2.5 effect
                0.01 * pm10 +  # PM10 effect
                -0.05 * temp +  # Cold temperature increases risk
                0.02 * humidity +  # High humidity increases risk
                0.1 * np.sin(2 * np.pi * date_val.timetuple().tm_yday / 365.25 + np.pi)  # Winter peak
            )
            
            # Convert to case rate per 100,000
            flu_base_rate = max(0, 5 + flu_risk * 10)
            daily_flu_cases = np.random.poisson(flu_base_rate * population / 100000 / 365)
            
            if daily_flu_cases > 0:
                for case_id in range(daily_flu_cases):
                    disease_data['influenza'].append({
                        'case_id': f"FLU_{date_val.strftime('%Y%m%d')}_{istat_code}_{case_id:03d}",
                        'case_date': date_val,
                        'istat_code': istat_code,
                        'disease_type': 'influenza',
                        'patient_age': max(0, int(np.random.normal(35, 20))),
                        'patient_gender': np.random.choice(['M', 'F']),
                        'severity': np.random.choice(['mild', 'moderate', 'severe'], p=[0.7, 0.25, 0.05]),
                        'outcome': 'active',
                        'environmental_exposure': {
                            'pm25': pm25,
                            'pm10': pm10,
                            'temperature': temp,
                            'humidity': humidity
                        },
                        'data_source': 'SYNTHETIC_MMG'
                    })
            
            # LEGIONELLOSIS CASES (Water-aerosol - temperature/humidity correlation)
            water_temp = row.get('water_temperature', 15)
            precipitation = row.get('precipitation', 0)
            
            # Legionellosis model: warm water, high humidity, recent rain
            legionella_risk = (
                0.1 * max(0, water_temp - 20) +  # Warm water increases risk
                0.03 * humidity +  # High humidity
                0.05 * min(precipitation, 20)  # Recent precipitation (capped)
            )
            
            # Very low base rate (rare disease)
            legionella_base_rate = max(0, 0.5 + legionella_risk)
            daily_legionella_cases = np.random.poisson(legionella_base_rate * population / 100000 / 365)
            
            if daily_legionella_cases > 0:
                for case_id in range(daily_legionella_cases):
                    disease_data['legionellosis'].append({
                        'case_id': f"LEG_{date_val.strftime('%Y%m%d')}_{istat_code}_{case_id:03d}",
                        'case_date': date_val,
                        'istat_code': istat_code,
                        'disease_type': 'legionellosis',
                        'patient_age': max(40, int(np.random.normal(65, 15))),  # Older adults more affected
                        'patient_gender': np.random.choice(['M', 'F'], p=[0.6, 0.4]),  # Slight male predominance
                        'severity': np.random.choice(['moderate', 'severe'], p=[0.3, 0.7]),
                        'outcome': np.random.choice(['active', 'recovered'], p=[0.8, 0.2]),
                        'environmental_exposure': {
                            'water_temperature': water_temp,
                            'humidity': humidity,
                            'precipitation': precipitation,
                            'water_ph': row.get('ph', 7.2)
                        },
                        'data_source': 'SYNTHETIC_HOSPITAL'
                    })
            
            # HEPATITIS A CASES (Foodborne/waterborne - water quality correlation)
            ecoli = row.get('ecoli_count', 10)
            ph_val = row.get('ph', 7.2)
            chlorine = row.get('residual_chlorine', 0.5)
            
            # Hepatitis A model: high E.coli, extreme pH, low chlorine
            hep_a_risk = (
                0.02 * np.log(ecoli + 1) +  # Log of E.coli count
                0.5 * abs(ph_val - 7.0) +  # Deviation from neutral pH
                -0.3 * chlorine +  # Low chlorine increases risk
                0.1 * min(precipitation, 30) +  # Heavy rain events
                0.05 * np.sin(2 * np.pi * date_val.timetuple().tm_yday / 365.25 - np.pi/2)  # Autumn peak
            )
            
            # Low base rate
            hep_a_base_rate = max(0, 1 + hep_a_risk * 2)
            daily_hep_a_cases = np.random.poisson(hep_a_base_rate * population / 100000 / 365)
            
            if daily_hep_a_cases > 0:
                for case_id in range(daily_hep_a_cases):
                    disease_data['hepatitis_a'].append({
                        'case_id': f"HEP_{date_val.strftime('%Y%m%d')}_{istat_code}_{case_id:03d}",
                        'case_date': date_val,
                        'istat_code': istat_code,
                        'disease_type': 'hepatitis_a',
                        'patient_age': max(5, int(np.random.normal(25, 15))),  # Younger adults more affected
                        'patient_gender': np.random.choice(['M', 'F']),
                        'severity': np.random.choice(['mild', 'moderate'], p=[0.8, 0.2]),
                        'outcome': np.random.choice(['active', 'recovered'], p=[0.7, 0.3]),
                        'environmental_exposure': {
                            'ecoli_count': ecoli,
                            'ph': ph_val,
                            'residual_chlorine': chlorine,
                            'precipitation': precipitation
                        },
                        'data_source': 'SYNTHETIC_PLS'
                    })
        
        # Convert to DataFrames
        return {disease: pd.DataFrame(cases) for disease, cases in disease_data.items()}
    
    def generate_investigation_data(self, disease_cases: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Generate epidemiological investigation data"""
        
        investigations = []
        
        for disease_type, cases_df in disease_cases.items():
            # Sample 20% of severe cases for investigation
            if len(cases_df) > 0:
                severe_cases = cases_df[cases_df.get('severity', 'mild').isin(['severe', 'moderate'])]
                investigation_cases = severe_cases.sample(n=min(len(severe_cases), max(1, len(severe_cases) // 5)))
                
                for _, case in investigation_cases.iterrows():
                    investigations.append({
                        'investigation_id': f"INV_{case['case_id']}",
                        'case_id': case['case_id'],
                        'disease_type': disease_type,
                        'investigation_date': case['case_date'] + timedelta(days=np.random.randint(1, 7)),
                        'investigator_role': 'UOSD',
                        'istat_code': case['istat_code'],
                        'probable_source': self._get_probable_source(disease_type),
                        'environmental_investigation': True,
                        'contact_tracing': np.random.choice([True, False], p=[0.8, 0.2]),
                        'risk_factors': self._get_risk_factors(disease_type),
                        'outcome': np.random.choice(['completed', 'ongoing'], p=[0.7, 0.3]),
                        'data_source': 'SYNTHETIC_INVESTIGATION'
                    })
        
        return pd.DataFrame(investigations)
    
    def _get_probable_source(self, disease_type: str) -> str:
        """Get probable source based on disease type"""
        sources = {
            'influenza': ['community_transmission', 'school_outbreak', 'workplace', 'household'],
            'legionellosis': ['cooling_tower', 'water_system', 'hot_tub', 'hospital_water', 'hotel'],
            'hepatitis_a': ['contaminated_water', 'food_outbreak', 'person_to_person', 'travel_related']
        }
        return np.random.choice(sources.get(disease_type, ['unknown']))
    
    def _get_risk_factors(self, disease_type: str) -> List[str]:
        """Get risk factors based on disease type"""
        factors = {
            'influenza': ['age_over_65', 'chronic_disease', 'immunocompromised', 'pregnancy'],
            'legionellosis': ['age_over_50', 'smoking', 'immunocompromised', 'chronic_lung_disease'],
            'hepatitis_a': ['poor_sanitation', 'travel_history', 'close_contact', 'food_handler']
        }
        available_factors = factors.get(disease_type, [])
        num_factors = np.random.randint(0, min(3, len(available_factors)))
        return np.random.choice(available_factors, size=num_factors, replace=False).tolist()
    
    def save_synthetic_data(self, output_dir: str = "synthetic_data"):
        """Generate and save all synthetic datasets"""
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print("🔄 Generating synthetic environmental data...")
        environmental_df = self.generate_environmental_data()
        
        print("🔄 Generating synthetic disease cases...")
        disease_cases = self.generate_disease_cases(environmental_df)
        
        print("🔄 Generating synthetic investigation data...")
        investigations_df = self.generate_investigation_data(disease_cases)
        
        # Save environmental data
        environmental_df.to_csv(output_path / "environmental_data.csv", index=False)
        environmental_df.to_json(output_path / "environmental_data.json", orient='records', date_format='iso')
        
        # Save disease cases
        for disease, df in disease_cases.items():
            df.to_csv(output_path / f"{disease}_cases.csv", index=False)
            df.to_json(output_path / f"{disease}_cases.json", orient='records', date_format='iso')
        
        # Save investigations
        investigations_df.to_csv(output_path / "investigations.csv", index=False)
        investigations_df.to_json(output_path / "investigations.json", orient='records', date_format='iso')
        
        # Generate summary statistics
        summary = self._generate_summary_stats(environmental_df, disease_cases, investigations_df)
        with open(output_path / "summary_statistics.json", 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"✅ Synthetic data generated successfully in '{output_dir}' directory!")
        print("\n📊 Data Summary:")
        print(f"   • Environmental records: {len(environmental_df):,}")
        print(f"   • Influenza cases: {len(disease_cases['influenza']):,}")
        print(f"   • Legionellosis cases: {len(disease_cases['legionellosis']):,}")
        print(f"   • Hepatitis A cases: {len(disease_cases['hepatitis_a']):,}")
        print(f"   • Investigations: {len(investigations_df):,}")
        print(f"   • Date range: {self.start_date.date()} to {self.end_date.date()}")
        print(f"   • ISTAT codes: {len(self.all_istat_codes)} locations")
        
        return {
            'environmental': environmental_df,
            'disease_cases': disease_cases,
            'investigations': investigations_df,
            'summary': summary
        }
    
    def _generate_summary_stats(self, env_df, disease_cases, investigations_df):
        """Generate summary statistics for the synthetic data"""
        
        return {
            "generation_date": datetime.now().isoformat(),
            "data_period": {
                "start_date": self.start_date.date().isoformat(),
                "end_date": self.end_date.date().isoformat(),
                "total_days": len(self.date_range)
            },
            "geographic_coverage": {
                "total_istat_codes": len(self.all_istat_codes),
                "regions": list(self.istat_codes.keys()),
                "istat_codes_by_region": self.istat_codes
            },
            "environmental_data": {
                "total_records": len(env_df),
                "parameters": {
                    "air_quality": self.pollutants,
                    "climate": self.climate_params,
                    "water_quality": self.water_params
                },
                "data_sources": env_df['data_source'].value_counts().to_dict()
            },
            "disease_cases": {
                disease: {
                    "total_cases": len(df),
                    "cases_per_month": df.groupby(df['case_date'].dt.to_period('M')).size().to_dict() if len(df) > 0 else {},
                    "severity_distribution": df['severity'].value_counts().to_dict() if len(df) > 0 else {},
                    "age_statistics": {
                        "mean": df['patient_age'].mean() if len(df) > 0 else 0,
                        "std": df['patient_age'].std() if len(df) > 0 else 0
                    }
                }
                for disease, df in disease_cases.items()
            },
            "investigations": {
                "total_investigations": len(investigations_df),
                "by_disease": investigations_df['disease_type'].value_counts().to_dict() if len(investigations_df) > 0 else {},
                "outcomes": investigations_df['outcome'].value_counts().to_dict() if len(investigations_df) > 0 else {}
            }
        }


if __name__ == "__main__":
    # Generate synthetic data
    generator = SyntheticDataGenerator()
    
    # Create synthetic datasets
    output_directory = "/home/amir/Documents/amir/Ambientale/HealthTrace/synthetic_data"
    synthetic_data = generator.save_synthetic_data(output_directory)
    
    print("\n🎯 Synthetic data is ready for testing all models and the HealthTrace app!")
    print("   Files created:")
    print("   • environmental_data.csv/.json - Air quality, climate, water data")
    print("   • influenza_cases.csv/.json - Flu cases with PM2.5/temperature correlation")
    print("   • legionellosis_cases.csv/.json - Legionella cases with water/humidity correlation") 
    print("   • hepatitis_a_cases.csv/.json - Hepatitis A cases with water quality correlation")
    print("   • investigations.csv/.json - Epidemiological investigations")
    print("   • summary_statistics.json - Complete data overview")
