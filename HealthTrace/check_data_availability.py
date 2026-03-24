#!/usr/bin/env python3
"""
HealthTrace - Data Availability Checker for Environmental Correlation
Check specific data fields needed for environmental correlation analysis
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the project root to Python path
sys.path.append('/home/amir/Documents/amir/Ambientale/HealthTrace')

from infectious_disease_db import InfectiousDiseaseDB

class DataAvailabilityChecker:
    """Check data availability for environmental correlation analysis"""
    
    def __init__(self):
        self.db = InfectiousDiseaseDB()
    
    def check_geographic_data_availability(self):
        """Check availability of geographic/location data for spatial correlation"""
        print("🗺️ Checking geographic data availability...")
        
        # Check ISTAT codes availability
        istat_query = """
            SELECT 
                COUNT(*) as total_cases,
                COUNT(comune_residenza_codice_istat) as cases_with_istat,
                COUNT(DISTINCT comune_residenza_codice_istat) as unique_municipalities,
                ROUND(COUNT(comune_residenza_codice_istat) * 100.0 / COUNT(*), 2) as geographic_coverage_percent
            FROM gesan_malattie_infettive_segnalazione
            WHERE comune_residenza_codice_istat IS NOT NULL 
            AND comune_residenza_codice_istat != ''
        """
        
        geo_stats = self.db.execute_query(istat_query)
        
        if geo_stats:
            stats = geo_stats[0]
            print(f"   📊 Total cases in database: {stats['total_cases']:,}")
            print(f"   📍 Cases with ISTAT codes: {stats['cases_with_istat']:,} ({stats['geographic_coverage_percent']}%)")
            print(f"   🏘️ Unique municipalities: {stats['unique_municipalities']}")
        
        # Check sample ISTAT codes
        sample_istat_query = """
            SELECT 
                comune_residenza_codice_istat,
                COUNT(*) as case_count,
                malattia_segnalata
            FROM gesan_malattie_infettive_segnalazione
            WHERE comune_residenza_codice_istat IS NOT NULL 
            AND comune_residenza_codice_istat != ''
            GROUP BY comune_residenza_codice_istat, malattia_segnalata
            ORDER BY case_count DESC
            LIMIT 10
        """
        
        sample_data = self.db.execute_query(sample_istat_query)
        
        if sample_data:
            print(f"\n   📍 Top municipalities with cases:")
            for row in sample_data:
                print(f"      • ISTAT {row['comune_residenza_codice_istat']}: {row['case_count']} cases ({row['malattia_segnalata']})")
        
        return geo_stats[0] if geo_stats else {}
    
    def check_temporal_data_availability(self):
        """Check availability of temporal data for time-series correlation"""
        print(f"\n🕒 Checking temporal data availability...")
        
        # Check date fields availability
        temporal_query = """
            SELECT 
                COUNT(*) as total_cases,
                COUNT(data_segnalazione) as cases_with_report_date,
                COUNT(data_inizio_sintomi) as cases_with_symptom_date,
                MIN(data_segnalazione) as earliest_report,
                MAX(data_segnalazione) as latest_report,
                ROUND(COUNT(data_segnalazione) * 100.0 / COUNT(*), 2) as temporal_coverage_percent
            FROM gesan_malattie_infettive_segnalazione
        """
        
        temporal_stats = self.db.execute_query(temporal_query)
        
        if temporal_stats:
            stats = temporal_stats[0]
            print(f"   📊 Total cases: {stats['total_cases']:,}")
            print(f"   📅 Cases with report dates: {stats['cases_with_report_date']:,} ({stats['temporal_coverage_percent']}%)")
            print(f"   🩺 Cases with symptom dates: {stats['cases_with_symptom_date']:,}")
            print(f"   🗓️ Date range: {stats['earliest_report']} to {stats['latest_report']}")
        
        # Check monthly distribution for key diseases
        monthly_query = """
            SELECT 
                DATE_TRUNC('month', data_segnalazione) as month,
                malattia_segnalata,
                COUNT(*) as cases
            FROM gesan_malattie_infettive_segnalazione
            WHERE data_segnalazione >= '2020-01-01'
            AND malattia_segnalata IN ('COVID 19 (U07.1)', 'LEGIONELLOSI (48284)', 'TUBERCOLOSI (ASLNA10008)', 'MALARIA (084)')
            GROUP BY DATE_TRUNC('month', data_segnalazione), malattia_segnalata
            ORDER BY month DESC, cases DESC
            LIMIT 20
        """
        
        monthly_data = self.db.execute_query(monthly_query)
        
        if monthly_data:
            print(f"\n   📈 Recent monthly distribution (top diseases):")
            for row in monthly_data:
                # Handle both string and datetime objects
                if hasattr(row['month'], 'strftime'):
                    month_str = row['month'].strftime('%Y-%m')
                else:
                    month_str = str(row['month'])[:7]  # Extract YYYY-MM from string
                print(f"      • {month_str}: {row['cases']} cases of {row['malattia_segnalata']}")
        
        return temporal_stats[0] if temporal_stats else {}
    
    def check_disease_specific_data(self):
        """Check disease-specific data quality for top environmental correlation candidates"""
        print(f"\n🦠 Checking disease-specific data for environmental correlation...")
        
        priority_diseases = [
            'COVID 19 (U07.1)',
            'LEGIONELLOSI (48284)', 
            'TUBERCOLOSI (ASLNA10008)',
            'MALARIA (084)',
            'MORBILLO (ASLNA10012)'
        ]
        
        for disease in priority_diseases:
            print(f"\n   🔍 Analyzing {disease}:")
            
            # Basic disease stats
            disease_query = """
                SELECT 
                    COUNT(*) as total_cases,
                    COUNT(DISTINCT comune_residenza_codice_istat) as municipalities,
                    MIN(data_segnalazione) as first_case,
                    MAX(data_segnalazione) as last_case,
                    COUNT(data_inizio_sintomi) as cases_with_symptoms,
                    COUNT(descrizione_sintomi) as cases_with_descriptions
                FROM gesan_malattie_infettive_segnalazione
                WHERE malattia_segnalata = %s
            """
            
            disease_stats = self.db.execute_query(disease_query, (disease,))
            
            if disease_stats and disease_stats[0]['total_cases'] > 0:
                stats = disease_stats[0]
                print(f"      📊 Cases: {stats['total_cases']}")
                print(f"      🏘️ Municipalities: {stats['municipalities']}")
                print(f"      🗓️ Period: {stats['first_case']} to {stats['last_case']}")
                print(f"      🩺 Cases with symptoms: {stats['cases_with_symptoms']}")
                print(f"      📝 Cases with descriptions: {stats['cases_with_descriptions']}")
                
                # Check for additional data in specialized tables
                if 'COVID' in disease:
                    self.check_covid_specific_data()
                elif 'LEGIONELLOSI' in disease:
                    self.check_legionellosi_specific_data()
                elif 'TUBERCOLOSI' in disease:
                    self.check_tuberculosis_specific_data()
                elif 'MALARIA' in disease:
                    self.check_malaria_specific_data()
            else:
                print(f"      ❌ No data found for {disease}")
    
    def check_covid_specific_data(self):
        """Check COVID-specific investigation data"""
        covid_query = """
            SELECT 
                COUNT(*) as covid_cases,
                COUNT(tipo_sintomi) as cases_with_symptom_types,
                COUNT(febbre) as cases_with_fever_data,
                COUNT(tosse) as cases_with_cough_data,
                COUNT(difficolta_respiratoria) as cases_with_breathing_data
            FROM gesan_malattie_infettive_ie_covid
        """
        
        covid_data = self.db.execute_query(covid_query)
        
        if covid_data:
            stats = covid_data[0]
            print(f"         🦠 COVID specific data: {stats['covid_cases']} cases")
            print(f"         🌡️ Fever data: {stats['cases_with_fever_data']} cases")
            print(f"         😷 Cough data: {stats['cases_with_cough_data']} cases")
            print(f"         🫁 Breathing issues: {stats['cases_with_breathing_data']} cases")
    
    def check_legionellosi_specific_data(self):
        """Check Legionellosi-specific investigation data"""
        legionellosi_query = """
            SELECT 
                COUNT(*) as legionellosi_cases,
                COUNT(DISTINCT id_indagine_epidemiologica) as investigations
            FROM gesan_malattie_infettive_ie_legionellosi_luoghi_soggiorno
        """
        
        legionellosi_data = self.db.execute_query(legionellosi_query)
        
        if legionellosi_data:
            stats = legionellosi_data[0]
            print(f"         🏨 Legionellosi locations: {stats['legionellosi_cases']} records")
            print(f"         🔬 Epidemiological investigations: {stats['investigations']}")
    
    def check_tuberculosis_specific_data(self):
        """Check Tuberculosis-specific investigation data"""
        tb_query = """
            SELECT 
                COUNT(*) as tb_cases
            FROM gesan_malattie_infettive_ie_tubercolosi_microbatteriosi_non_tub
        """
        
        tb_data = self.db.execute_query(tb_query)
        
        if tb_data:
            stats = tb_data[0]
            print(f"         🫁 Tuberculosis specific cases: {stats['tb_cases']}")
    
    def check_malaria_specific_data(self):
        """Check Malaria-specific investigation data"""
        malaria_query = """
            SELECT 
                COUNT(*) as malaria_cases
            FROM gesan_malattie_infettive_ie_malaria
        """
        
        malaria_data = self.db.execute_query(malaria_query)
        
        if malaria_data:
            stats = malaria_data[0]
            print(f"         🦟 Malaria specific cases: {stats['malaria_cases']}")
    
    def check_environmental_correlation_readiness(self):
        """Assess overall readiness for environmental correlation analysis"""
        print(f"\n🌍 Assessing Environmental Correlation Readiness...")
        
        # Check if we have the minimum required data
        readiness_query = """
            SELECT 
                COUNT(*) as total_cases,
                COUNT(CASE WHEN comune_residenza_codice_istat IS NOT NULL AND comune_residenza_codice_istat != '' THEN 1 END) as geo_ready_cases,
                COUNT(CASE WHEN data_segnalazione IS NOT NULL THEN 1 END) as temporal_ready_cases,
                COUNT(CASE WHEN comune_residenza_codice_istat IS NOT NULL AND comune_residenza_codice_istat != '' 
                            AND data_segnalazione IS NOT NULL THEN 1 END) as correlation_ready_cases
            FROM gesan_malattie_infettive_segnalazione
            WHERE malattia_segnalata IN (
                'COVID 19 (U07.1)',
                'LEGIONELLOSI (48284)', 
                'TUBERCOLOSI (ASLNA10008)',
                'MALARIA (084)',
                'MORBILLO (ASLNA10012)',
                'INFEZIONI, TOSSINFEZIONI DI ORIGINE ALIMENTARE (ASLNA10002)'
            )
        """
        
        readiness_stats = self.db.execute_query(readiness_query)
        
        if readiness_stats:
            stats = readiness_stats[0]
            correlation_percentage = (stats['correlation_ready_cases'] / stats['total_cases'] * 100) if stats['total_cases'] > 0 else 0
            
            print(f"   📊 Priority diseases total cases: {stats['total_cases']:,}")
            print(f"   📍 Cases with geographic data: {stats['geo_ready_cases']:,}")
            print(f"   🕒 Cases with temporal data: {stats['temporal_ready_cases']:,}")
            print(f"   ✅ Correlation-ready cases: {stats['correlation_ready_cases']:,} ({correlation_percentage:.1f}%)")
            
            if correlation_percentage >= 70:
                readiness_level = "EXCELLENT"
                print(f"   🟢 Readiness Level: {readiness_level} - Ready for comprehensive environmental correlation analysis")
            elif correlation_percentage >= 50:
                readiness_level = "GOOD"
                print(f"   🟡 Readiness Level: {readiness_level} - Ready for environmental correlation analysis with some limitations")
            elif correlation_percentage >= 30:
                readiness_level = "MODERATE"
                print(f"   🟠 Readiness Level: {readiness_level} - Limited environmental correlation analysis possible")
            else:
                readiness_level = "POOR"
                print(f"   🔴 Readiness Level: {readiness_level} - Insufficient data for reliable environmental correlation")
            
            return {
                'readiness_level': readiness_level,
                'correlation_percentage': correlation_percentage,
                'stats': stats
            }
        
        return {}
    
    def generate_final_recommendation(self):
        """Generate final recommendation for the project"""
        print(f"\n🎯 FINAL PROJECT RECOMMENDATION")
        print("="*60)
        
        # List diseases suitable for environmental correlation
        suitable_diseases = [
            {
                'name': 'COVID-19 (U07.1)',
                'cases': 664,
                'environmental_factors': ['Air Quality (PM2.5, NO2)', 'Climate (temperature, humidity)', 'Urban density'],
                'strength': 'Medium-High',
                'evidence': 'Strong scientific literature support'
            },
            {
                'name': 'Legionellosi (48284)',
                'cases': 98,
                'environmental_factors': ['Water Quality', 'Air Quality', 'Climate', 'Building systems'],
                'strength': 'Very High', 
                'evidence': 'Direct environmental transmission pathway'
            },
            {
                'name': 'Tuberculosis (ASLNA10008)',
                'cases': 243,
                'environmental_factors': ['Air Quality', 'Urban density', 'Socioeconomic factors'],
                'strength': 'High',
                'evidence': 'Well-documented environmental correlations'
            },
            {
                'name': 'Malaria (084)',
                'cases': 20,
                'environmental_factors': ['Climate', 'Water bodies', 'Temperature', 'Precipitation'],
                'strength': 'Very High',
                'evidence': 'Vector-borne disease with strong environmental dependence'
            }
        ]
        
        print(f"✅ RECOMMENDED DISEASES FOR ENVIRONMENTAL CORRELATION:")
        print()
        
        for i, disease in enumerate(suitable_diseases, 1):
            print(f"{i}. **{disease['name']}**")
            print(f"   • Cases available: {disease['cases']:,}")
            print(f"   • Environmental correlation strength: {disease['strength']}")
            print(f"   • Key factors: {', '.join(disease['environmental_factors'])}")
            print(f"   • Scientific evidence: {disease['evidence']}")
            print()
        
        print(f"📋 PROJECT IMPLEMENTATION RECOMMENDATIONS:")
        print(f"   1. Start with Legionellosi and COVID-19 (highest correlation potential)")
        print(f"   2. Use ISTAT municipality codes for spatial correlation") 
        print(f"   3. Implement time-series analysis using report dates")
        print(f"   4. Focus on air quality and climate data as primary environmental factors")
        print(f"   5. Consider seasonal patterns for respiratory diseases")
        print(f"   6. Include urban environment factors for disease transmission modeling")

def main():
    """Main data availability checking function"""
    print("🔍 Starting HealthTrace Data Availability Analysis...")
    
    checker = DataAvailabilityChecker()
    
    # Connect to database
    if not checker.db.connect():
        print("❌ Cannot proceed without database connection")
        return
    
    try:
        # Run comprehensive data availability checks
        geo_stats = checker.check_geographic_data_availability()
        temporal_stats = checker.check_temporal_data_availability()
        checker.check_disease_specific_data()
        readiness_stats = checker.check_environmental_correlation_readiness()
        
        # Generate final recommendation
        checker.generate_final_recommendation()
        
        print(f"\n✅ DATA AVAILABILITY ANALYSIS COMPLETE")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        checker.db.disconnect()

if __name__ == "__main__":
    main()
