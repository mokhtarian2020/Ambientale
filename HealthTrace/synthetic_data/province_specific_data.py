#!/usr/bin/env python3
"""
Province-Specific Synthetic Data Generator for HealthTrace
Generates realistic environmental and health data for each province in Campania, Calabria, and Molise
"""

import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Province definitions with characteristics
PROVINCES = {
    'Campania': {
        'Napoli': {
            'population': 3100000,
            'urban_density': 'very_high',
            'coastal': True,
            'industrial': True,
            'pm25_base': 28.5,
            'temperature_base': 19.2,
            'humidity_base': 68.5
        },
        'Salerno': {
            'population': 1100000,
            'urban_density': 'medium',
            'coastal': True,
            'industrial': False,
            'pm25_base': 22.1,
            'temperature_base': 18.8,
            'humidity_base': 65.2
        },
        'Avellino': {
            'population': 420000,
            'urban_density': 'low',
            'coastal': False,
            'industrial': False,
            'pm25_base': 18.3,
            'temperature_base': 16.5,
            'humidity_base': 62.8
        },
        'Benevento': {
            'population': 280000,
            'urban_density': 'low',
            'coastal': False,
            'industrial': False,
            'pm25_base': 19.7,
            'temperature_base': 17.1,
            'humidity_base': 63.5
        },
        'Caserta': {
            'population': 920000,
            'urban_density': 'medium',
            'coastal': False,
            'industrial': True,
            'pm25_base': 25.2,
            'temperature_base': 18.3,
            'humidity_base': 66.1
        }
    },
    'Calabria': {
        'Catanzaro': {
            'population': 360000,
            'urban_density': 'medium',
            'coastal': True,
            'industrial': False,
            'pm25_base': 16.8,
            'temperature_base': 20.5,
            'humidity_base': 71.2
        },
        'Cosenza': {
            'population': 700000,
            'urban_density': 'medium',
            'coastal': False,
            'industrial': False,
            'pm25_base': 18.5,
            'temperature_base': 18.9,
            'humidity_base': 68.7
        },
        'Crotone': {
            'population': 175000,
            'urban_density': 'low',
            'coastal': True,
            'industrial': True,
            'pm25_base': 21.3,
            'temperature_base': 21.1,
            'humidity_base': 73.4
        },
        'Reggio Calabria': {
            'population': 550000,
            'urban_density': 'medium',
            'coastal': True,
            'industrial': False,
            'pm25_base': 19.2,
            'temperature_base': 21.8,
            'humidity_base': 74.8
        },
        'Vibo Valentia': {
            'population': 160000,
            'urban_density': 'low',
            'coastal': True,
            'industrial': False,
            'pm25_base': 15.4,
            'temperature_base': 20.9,
            'humidity_base': 72.6
        }
    },
    'Molise': {
        'Campobasso': {
            'population': 225000,
            'urban_density': 'low',
            'coastal': False,
            'industrial': False,
            'pm25_base': 14.2,
            'temperature_base': 15.8,
            'humidity_base': 59.3
        },
        'Isernia': {
            'population': 85000,
            'urban_density': 'very_low',
            'coastal': False,
            'industrial': False,
            'pm25_base': 12.8,
            'temperature_base': 14.9,
            'humidity_base': 57.1
        }
    }
}

class ProvinceDataGenerator:
    def __init__(self):
        self.months = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 
                      'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic']
        
    def generate_environmental_data(self, province_info: Dict) -> List[Dict]:
        """Generate monthly environmental data for a province"""
        data = []
        pm25_base = province_info['pm25_base']
        temp_base = province_info['temperature_base']
        humidity_base = province_info['humidity_base']
        
        for i, month in enumerate(self.months):
            # Seasonal variations
            temp_seasonal = temp_base + 10 * np.sin((i - 6) * np.pi / 6)
            pm25_seasonal = pm25_base + 8 * np.sin((i + 3) * np.pi / 6)  # Higher in winter
            humidity_seasonal = humidity_base + 15 * np.sin((i - 3) * np.pi / 6)
            
            # Add random variation
            data.append({
                'month': month,
                'pm25': round(max(5, pm25_seasonal + random.gauss(0, 3)), 1),
                'no2': round(max(8, pm25_seasonal * 0.8 + random.gauss(0, 2)), 1),
                'o3': round(max(15, 45 - pm25_seasonal * 0.5 + random.gauss(0, 4)), 1),
                'temperature': round(temp_seasonal + random.gauss(0, 2), 1),
                'humidity': round(max(30, min(95, humidity_seasonal + random.gauss(0, 5))), 1),
                'ecoli': round(max(0, np.random.exponential(15)), 1)
            })
        
        return data
    
    def generate_disease_data(self, province_info: Dict, environmental_data: List[Dict]) -> List[Dict]:
        """Generate disease cases correlated with environmental factors"""
        data = []
        population_factor = province_info['population'] / 1000000  # Scale to millions
        
        for i, (month_data, env_data) in enumerate(zip(self.months, environmental_data)):
            # Disease correlations
            # Influenza: higher with PM2.5 and lower temperature
            influenza_base = max(0, (env_data['pm25'] - 15) * 2 + (20 - env_data['temperature']) * 1.5)
            influenza_cases = max(0, int(population_factor * (influenza_base + random.gauss(0, 5))))
            
            # Legionellosis: higher with temperature and humidity
            legionella_base = max(0, (env_data['temperature'] - 15) * 0.3 + (env_data['humidity'] - 60) * 0.2)
            legionella_cases = max(0, int(population_factor * (legionella_base + random.gauss(0, 2))))
            
            # Hepatitis A: correlated with E.coli (water contamination)
            hepatitis_base = max(0, env_data['ecoli'] * 0.05)
            hepatitis_cases = max(0, int(population_factor * (hepatitis_base + random.gauss(0, 1))))
            
            data.append({
                'month': month_data,
                'influenza_cases': influenza_cases,
                'legionellosis_cases': legionella_cases,
                'hepatitis_a_cases': hepatitis_cases,
                'total_cases': influenza_cases + legionella_cases + hepatitis_cases,
                **env_data
            })
        
        return data
    
    def calculate_correlations(self, data: List[Dict]) -> Dict:
        """Calculate correlation coefficients between environmental factors and diseases"""
        pm25_values = [d['pm25'] for d in data]
        temp_values = [d['temperature'] for d in data]
        ecoli_values = [d['ecoli'] for d in data]
        
        influenza_values = [d['influenza_cases'] for d in data]
        legionella_values = [d['legionellosis_cases'] for d in data]
        hepatitis_values = [d['hepatitis_a_cases'] for d in data]
        
        def correlation(x, y):
            return np.corrcoef(x, y)[0, 1] if len(set(x)) > 1 and len(set(y)) > 1 else 0
        
        return {
            'pm25_influenza': round(correlation(pm25_values, influenza_values), 2),
            'temperature_legionella': round(correlation(temp_values, legionella_values), 2),
            'ecoli_hepatitis': round(correlation(ecoli_values, hepatitis_values), 2),
            'pm25_respiratory': round(correlation(pm25_values, influenza_values), 2),
            'temperature_infectious': round(correlation(temp_values, 
                [i + l for i, l in zip(influenza_values, legionella_values)]), 2)
        }
    
    def generate_correlation_scatter_data(self, province_info: Dict) -> Dict:
        """Generate scatter plot data for correlations"""
        # PM2.5 vs Influenza scatter data
        pm25_influenza = []
        for _ in range(24):
            pm25 = province_info['pm25_base'] + random.gauss(0, 8)
            influenza = max(0, (pm25 - 15) * 0.8 + random.gauss(0, 3))
            pm25_influenza.append({'x': round(pm25, 1), 'y': round(influenza, 1)})
        
        # Temperature vs Legionella scatter data
        temp_legionella = []
        for _ in range(24):
            temp = province_info['temperature_base'] + random.gauss(0, 6)
            legionella = max(0, (temp - 15) * 0.3 + random.gauss(0, 1))
            temp_legionella.append({'x': round(temp, 1), 'y': round(legionella, 1)})
        
        # E.coli vs Hepatitis scatter data
        ecoli_hepatitis = []
        for _ in range(20):
            ecoli = np.random.exponential(20)
            hepatitis = max(0, ecoli * 0.05 + random.gauss(0, 0.5))
            ecoli_hepatitis.append({'x': round(ecoli, 1), 'y': round(hepatitis, 1)})
        
        return {
            'pm25_influenza': pm25_influenza,
            'temperature_legionella': temp_legionella,
            'ecoli_hepatitis': ecoli_hepatitis
        }
    
    def generate_province_dataset(self, region: str, province: str) -> Dict:
        """Generate complete dataset for a specific province"""
        province_info = PROVINCES[region][province]
        
        # Generate environmental and disease data
        environmental_data = self.generate_environmental_data(province_info)
        monthly_data = self.generate_disease_data(province_info, environmental_data)
        
        # Calculate correlations
        correlations = self.calculate_correlations(monthly_data)
        
        # Generate scatter plot data
        scatter_data = self.generate_correlation_scatter_data(province_info)
        
        # Calculate totals
        total_cases = sum(d['total_cases'] for d in monthly_data)
        total_influenza = sum(d['influenza_cases'] for d in monthly_data)
        total_legionella = sum(d['legionellosis_cases'] for d in monthly_data)
        total_hepatitis = sum(d['hepatitis_a_cases'] for d in monthly_data)
        
        return {
            'province_info': {
                'name': province,
                'region': region,
                'population': province_info['population'],
                'characteristics': {
                    'urban_density': province_info['urban_density'],
                    'coastal': province_info['coastal'],
                    'industrial': province_info['industrial']
                }
            },
            'summary': {
                'total_cases': total_cases,
                'total_influenza': total_influenza,
                'total_legionella': total_legionella,
                'total_hepatitis': total_hepatitis,
                'avg_pm25': round(np.mean([d['pm25'] for d in monthly_data]), 1),
                'avg_temperature': round(np.mean([d['temperature'] for d in monthly_data]), 1)
            },
            'monthly_data': monthly_data,
            'correlations': correlations,
            'scatter_data': scatter_data,
            'last_updated': datetime.now().isoformat()
        }
    
    def generate_all_provinces(self) -> Dict:
        """Generate datasets for all provinces"""
        all_data = {}
        
        for region, provinces in PROVINCES.items():
            all_data[region] = {}
            for province in provinces:
                all_data[region][province] = self.generate_province_dataset(region, province)
        
        return {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '1.0.0',
                'total_provinces': sum(len(provinces) for provinces in PROVINCES.values()),
                'regions': list(PROVINCES.keys())
            },
            'data': all_data
        }

def main():
    """Generate and save province-specific data"""
    generator = ProvinceDataGenerator()
    
    # Generate all province data
    all_province_data = generator.generate_all_provinces()
    
    # Save to JSON file
    output_file = '/home/amir/Documents/amir/Ambientale/HealthTrace/synthetic_data/province_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_province_data, f, indent=2, ensure_ascii=False)
    
    print(f"Province-specific data generated and saved to: {output_file}")
    
    # Print summary
    data = all_province_data['data']
    print("\n=== PROVINCE DATA SUMMARY ===")
    for region, provinces in data.items():
        print(f"\n{region}:")
        for province, pdata in provinces.items():
            summary = pdata['summary']
            print(f"  {province}: {summary['total_cases']} total cases, "
                  f"PM2.5: {summary['avg_pm25']}, Temp: {summary['avg_temperature']}°C")

if __name__ == "__main__":
    main()
