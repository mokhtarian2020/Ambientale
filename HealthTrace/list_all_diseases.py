#!/usr/bin/env python3
"""
Complete List of All Infectious Diseases in GESAN Database
Simple query to show all available diseases for environmental correlation project
"""

import sys
sys.path.append('/home/amir/Documents/amir/Ambientale/HealthTrace')

from infectious_disease_db import InfectiousDiseaseDB

def get_complete_diseases_list():
    """Get complete list of all diseases with basic statistics"""
    
    db = InfectiousDiseaseDB()
    
    if not db.connect():
        print("❌ Cannot connect to database")
        return
    
    try:
        # Query all diseases with basic stats
        query = """
            SELECT 
                malattia_segnalata,
                COUNT(*) as total_cases,
                MIN(data_segnalazione) as first_case,
                MAX(data_segnalazione) as last_case,
                COUNT(DISTINCT comune_residenza_codice_istat) as municipalities
            FROM gesan_malattie_infettive_segnalazione
            WHERE malattia_segnalata IS NOT NULL 
            AND malattia_segnalata != ''
            GROUP BY malattia_segnalata
            ORDER BY total_cases DESC
        """
        
        diseases = db.execute_query(query)
        
        print("🦠 COMPLETE LIST OF INFECTIOUS DISEASES IN HEALTHTRACE DATABASE")
        print("="*80)
        print(f"📊 Total Diseases Found: {len(diseases)}")
        print(f"📊 Total Cases: {sum(d['total_cases'] for d in diseases):,}")
        print("="*80)
        
        # Environmental correlation categories
        high_environmental = []
        medium_environmental = []
        low_environmental = []
        
        for i, disease in enumerate(diseases, 1):
            disease_name = disease['malattia_segnalata']
            cases = disease['total_cases']
            municipalities = disease['municipalities']
            
            # Categorize by environmental correlation potential
            if any(keyword in disease_name.lower() for keyword in ['legionell', 'covid', 'tubercol', 'malaria', 'epatite', 'alimentar']):
                category = "🟢 HIGH"
                high_environmental.append(disease)
            elif any(keyword in disease_name.lower() for keyword in ['influenza', 'morbillo', 'rosolia', 'meningite', 'pertosse']):
                category = "🟡 MEDIUM"  
                medium_environmental.append(disease)
            else:
                category = "🔴 LOW"
                low_environmental.append(disease)
            
            print(f"{i:2d}. {disease_name}")
            print(f"    📊 Cases: {cases:,} | 🏘️ Municipalities: {municipalities} | 🌍 Environmental: {category}")
            
        print("\n" + "="*80)
        print("🎯 ENVIRONMENTAL CORRELATION SUMMARY")
        print("="*80)
        print(f"🟢 HIGH Environmental Correlation Potential: {len(high_environmental)} diseases")
        print(f"🟡 MEDIUM Environmental Correlation Potential: {len(medium_environmental)} diseases") 
        print(f"🔴 LOW Environmental Correlation Potential: {len(low_environmental)} diseases")
        
        print(f"\n🥇 TOP 10 DISEASES BY CASE COUNT:")
        for i, disease in enumerate(diseases[:10], 1):
            print(f"   {i}. {disease['malattia_segnalata']} - {disease['total_cases']:,} cases")
            
        print(f"\n🌍 TOP ENVIRONMENTAL CORRELATION CANDIDATES:")
        high_environmental_sorted = sorted(high_environmental, key=lambda x: x['total_cases'], reverse=True)
        for i, disease in enumerate(high_environmental_sorted[:5], 1):
            print(f"   {i}. {disease['malattia_segnalata']} - {disease['total_cases']:,} cases")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    get_complete_diseases_list()
