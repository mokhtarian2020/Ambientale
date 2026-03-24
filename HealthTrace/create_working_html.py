#!/usr/bin/env python3
"""
Generate static HTML page with real database data for three diseases statistics
"""

import sys
import json
from datetime import datetime

sys.path.append('/home/amir/Documents/amir/Ambientale/HealthTrace')
from infectious_disease_db import InfectiousDiseaseDB

def get_three_diseases_data():
    """Get real data for the three priority diseases"""
    
    db = InfectiousDiseaseDB()
    
    if not db.connect():
        print("❌ Cannot connect to database")
        return None
    
    try:
        # Get data for the three main diseases
        diseases_query = """
            SELECT 
                malattia_segnalata,
                COUNT(*) as total_cases,
                COUNT(DISTINCT comune_residenza_codice_istat) as municipalities,
                MIN(data_segnalazione) as first_case,
                MAX(data_segnalazione) as last_case,
                comune_residenza_codice_istat,
                data_segnalazione,
                descrizione_sintomi
            FROM gesan_malattie_infettive_segnalazione
            WHERE malattia_segnalata IN (
                'LEGIONELLOSI (48284)',
                'EPATITE VIRALE A (0701)', 
                'INFLUENZA NON COMPLICATA (ASLNA12024000052)',
                'INFLUENZA - CASI GRAVI E COMPLICATI (487)'
            )
            GROUP BY malattia_segnalata, comune_residenza_codice_istat, data_segnalazione, descrizione_sintomi
            ORDER BY malattia_segnalata, data_segnalazione DESC
        """
        
        results = db.execute_query(diseases_query)
        
        # Process data for JavaScript
        diseases_data = {
            'legionellosi': {
                'name': 'Legionellosi',
                'cases': [],
                'total': 0,
                'municipalities': set()
            },
            'hepatitis_a': {
                'name': 'Epatite A', 
                'cases': [],
                'total': 0,
                'municipalities': set()
            },
            'influenza': {
                'name': 'Influenza',
                'cases': [],
                'total': 0,
                'municipalities': set()
            }
        }
        
        for row in results:
            disease_name = row['malattia_segnalata']
            
            if 'LEGIONELLOSI' in disease_name:
                key = 'legionellosi'
            elif 'EPATITE' in disease_name:
                key = 'hepatitis_a'
            elif 'INFLUENZA' in disease_name:
                key = 'influenza'
            else:
                continue
                
            case_data = {
                'istat_code': row['comune_residenza_codice_istat'],
                'date': row['data_segnalazione'],
                'symptoms': row['descrizione_sintomi'] or 'Sintomi non specificati'
            }
            
            diseases_data[key]['cases'].append(case_data)
            diseases_data[key]['municipalities'].add(row['comune_residenza_codice_istat'])
        
        # Calculate totals and convert sets to lists
        for key in diseases_data:
            diseases_data[key]['total'] = len(diseases_data[key]['cases'])
            diseases_data[key]['municipalities'] = len(diseases_data[key]['municipalities'])
        
        return diseases_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    
    finally:
        db.disconnect()

def create_static_html_with_data():
    """Create HTML file with embedded real data"""
    
    print("🔄 Getting real database data...")
    diseases_data = get_three_diseases_data()
    
    if not diseases_data:
        print("❌ Could not get data from database")
        return False
    
    print(f"✅ Data retrieved:")
    for key, data in diseases_data.items():
        print(f"   • {data['name']}: {data['total']} cases, {data['municipalities']} municipalities")
    
    # Read the original HTML file
    original_html = '/home/amir/Documents/amir/Ambientale/HealthTrace/three_diseases_statistics.html'
    
    with open(original_html, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Create the JavaScript data object
    js_data = json.dumps({
        'status': 'success',
        'data': {
            'legionellosi': {
                'name': 'Legionellosi',
                'total_cases': diseases_data['legionellosi']['total'],
                'municipalities_affected': diseases_data['legionellosi']['municipalities'],
                'cases_by_month': create_monthly_data(diseases_data['legionellosi']['cases']),
                'cases_by_municipality': create_municipality_data(diseases_data['legionellosi']['cases'])
            },
            'hepatitis_a': {
                'name': 'Epatite A',
                'total_cases': diseases_data['hepatitis_a']['total'],
                'municipalities_affected': diseases_data['hepatitis_a']['municipalities'],
                'cases_by_month': create_monthly_data(diseases_data['hepatitis_a']['cases']),
                'cases_by_municipality': create_municipality_data(diseases_data['hepatitis_a']['cases'])
            },
            'influenza': {
                'name': 'Influenza',
                'total_cases': diseases_data['influenza']['total'],
                'municipalities_affected': diseases_data['influenza']['municipalities'],
                'cases_by_month': create_monthly_data(diseases_data['influenza']['cases']),
                'cases_by_municipality': create_municipality_data(diseases_data['influenza']['cases'])
            }
        }
    }, indent=2, default=str)
    
    # Replace the fetch call with static data
    fetch_replacement = f"""
        async function loadData() {{
            try {{
                console.log('🔄 Loading static data...');
                
                // Static data from GESAN database
                diseaseData = {js_data};
                
                console.log('📊 Data loaded:', diseaseData ? 'SUCCESS' : 'FAILED');
                console.log('📋 Status:', diseaseData?.status);

                if (diseaseData.status === 'success') {{
                    normalizeDiseases();
                    console.log('🎨 Rendering overview...');
                    renderOverview();
                    console.log('📈 Rendering charts...');
                    renderCharts();
                    console.log('🗺️ Rendering map...');
                    renderMap();
                    console.log('📋 Rendering tables...');
                    renderTables();
                    
                    console.log('✅ Showing content...');
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('content').style.display = 'block';
                    if (map && typeof map.invalidateSize === 'function') {{
                        map.invalidateSize();
                    }}
                    console.log('🎉 Load complete!');
                }} else {{
                    throw new Error('Errore nel caricamento dei dati');
                }}
            }} catch (error) {{
                console.error('❌ Errore in loadData:', error);
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'block';
                document.getElementById('error').textContent = `Errore nel caricamento dei dati: ${{error.message}}`;
            }}
        }}"""
    
    # Find and replace the loadData function
    import re
    pattern = r'async function loadData\(\) \{[^}]+(?:\{[^}]*\}[^}]*)*\}'
    
    # Find the function more carefully
    start_pattern = r'async function loadData\(\) \{'
    start_match = re.search(start_pattern, html_content)
    
    if start_match:
        # Find the matching closing brace
        start_pos = start_match.start()
        brace_count = 0
        pos = start_match.end() - 1  # Start from the opening brace
        
        for i in range(pos, len(html_content)):
            if html_content[i] == '{':
                brace_count += 1
            elif html_content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i + 1
                    break
        
        # Replace the function
        new_html = html_content[:start_pos] + fetch_replacement + html_content[end_pos:]
        
        # Save the new file
        output_file = '/home/amir/Documents/amir/Ambientale/HealthTrace/three_diseases_statistics_WORKING.html'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(new_html)
        
        print(f"✅ Created working HTML file: {output_file}")
        return output_file
    
    else:
        print("❌ Could not find loadData function to replace")
        return False

def create_monthly_data(cases):
    """Create monthly aggregated data"""
    monthly = {}
    
    for case in cases:
        if case['date']:
            try:
                date_obj = datetime.fromisoformat(case['date'].replace('T', ' '))
                month_key = date_obj.strftime('%Y-%m')
                monthly[month_key] = monthly.get(month_key, 0) + 1
            except:
                continue
    
    return [{'month': k, 'cases': v} for k, v in sorted(monthly.items())]

def create_municipality_data(cases):
    """Create municipality aggregated data"""
    municipalities = {}
    
    for case in cases:
        istat = case['istat_code']
        if istat:
            municipalities[istat] = municipalities.get(istat, 0) + 1
    
    return [{'istat_code': k, 'cases': v} for k, v in sorted(municipalities.items(), key=lambda x: x[1], reverse=True)]

if __name__ == "__main__":
    output_file = create_static_html_with_data()
    if output_file:
        print(f"\n🚀 Opening the working HTML file...")
        import subprocess
        subprocess.run(['xdg-open', output_file])
    else:
        print("❌ Failed to create working HTML file")
