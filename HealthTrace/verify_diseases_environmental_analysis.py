#!/usr/bin/env python3
"""
HealthTrace - Infectious Diseases & Environmental Factors Analysis
Comprehensive analysis of available diseases and their environmental correlation potential
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the project root to Python path
sys.path.append('/home/amir/Documents/amir/Ambientale/HealthTrace')

from infectious_disease_db import InfectiousDiseaseDB

class EnvironmentalCorrelationAnalyzer:
    """Analyzer for infectious diseases with environmental correlation potential"""
    
    def __init__(self):
        self.db = InfectiousDiseaseDB()
        self.environmental_factors = {
            'air_quality': ['PM2.5', 'PM10', 'NO2', 'O3', 'SO2', 'CO'],
            'climate': ['temperature', 'humidity', 'precipitation', 'wind_speed'],
            'water_quality': ['bacterial_contamination', 'chemical_pollution'],
            'soil_quality': ['heavy_metals', 'pesticides', 'organic_pollutants'],
            'urban_environment': ['population_density', 'green_spaces', 'traffic_density']
        }
        
        # Disease categories with environmental correlation potential
        self.disease_categories = {
            'respiratory': ['legionellosi', 'influenza', 'tubercolosi', 'covid'],
            'foodborne': ['infezioni_alimentari', 'listeriosi', 'epatite_a', 'tossinfezioni'],
            'vectorborne': ['malaria', 'leishmaniosi'],
            'waterborne': ['legionellosi', 'epatite_a', 'epatite_e'],
            'airborne': ['morbillo', 'tubercolosi', 'influenza', 'covid'],
            'environmental': ['legionellosi', 'infezioni_alimentari', 'tetano']
        }
    
    def connect_database(self) -> bool:
        """Connect to the GESAN database"""
        print("🔌 Connecting to GESAN infectious diseases database...")
        if self.db.connect():
            print("✅ Successfully connected to database")
            return True
        else:
            print("❌ Failed to connect to database")
            return False
    
    def get_all_diseases_list(self) -> List[Dict[str, Any]]:
        """Get complete list of all diseases in the database"""
        print("\n📋 Retrieving complete list of diseases from database...")
        
        # Get disease statistics from main surveillance table
        diseases_query = """
            SELECT 
                malattia_segnalata,
                COUNT(*) as total_cases,
                MIN(data_segnalazione) as first_case_date,
                MAX(data_segnalazione) as last_case_date,
                COUNT(DISTINCT comune_residenza_codice_istat) as municipalities_affected
            FROM gesan_malattie_infettive_segnalazione
            WHERE malattia_segnalata IS NOT NULL 
            AND malattia_segnalata != ''
            GROUP BY malattia_segnalata
            ORDER BY total_cases DESC
        """
        
        diseases = self.db.execute_query(diseases_query)
        
        if diseases:
            print(f"✅ Found {len(diseases)} different diseases in surveillance system")
            
            # Add environmental correlation potential
            for disease in diseases:
                disease['environmental_correlation'] = self.assess_environmental_correlation(disease['malattia_segnalata'])
                disease['data_quality'] = self.assess_data_quality(disease)
                disease['project_suitability'] = self.assess_project_suitability(disease)
        
        return diseases
    
    def get_specialized_diseases_tables(self) -> List[Dict[str, Any]]:
        """Get diseases from specialized investigation tables"""
        print("\n🔬 Analyzing specialized disease investigation tables...")
        
        specialized_tables_query = """
            SELECT 
                table_name,
                (SELECT COUNT(*) FROM information_schema.columns 
                 WHERE table_name = t.table_name AND table_schema = 'public') as column_count
            FROM information_schema.tables t
            WHERE t.table_schema = 'public' 
            AND t.table_type = 'BASE TABLE'
            AND (t.table_name LIKE '%ie_%' OR t.table_name LIKE '%malattie_infettive%')
            AND t.table_name != 'gesan_malattie_infettive_segnalazione'
            ORDER BY t.table_name
        """
        
        tables = self.db.execute_query(specialized_tables_query)
        specialized_diseases = []
        
        for table in tables:
            try:
                # Get row count for each table
                count_query = f'SELECT COUNT(*) as row_count FROM "{table["table_name"]}"'
                count_result = self.db.execute_query(count_query)
                
                if count_result and count_result[0]['row_count'] > 0:
                    table['row_count'] = count_result[0]['row_count']
                    table['disease_name'] = self.extract_disease_from_table_name(table['table_name'])
                    table['environmental_potential'] = self.assess_table_environmental_potential(table['table_name'])
                    specialized_diseases.append(table)
                    
            except Exception as e:
                print(f"⚠️ Warning: Could not analyze table {table['table_name']}: {e}")
        
        print(f"✅ Found {len(specialized_diseases)} specialized disease tables with data")
        return specialized_diseases
    
    def assess_environmental_correlation(self, disease_name: str) -> Dict[str, Any]:
        """Assess environmental correlation potential for a disease"""
        disease_lower = disease_name.lower()
        
        correlation = {
            'potential': 'unknown',
            'factors': [],
            'strength': 0,
            'evidence_level': 'none'
        }
        
        # Strong environmental correlations
        if any(keyword in disease_lower for keyword in ['legionella', 'legionellosi']):
            correlation = {
                'potential': 'high',
                'factors': ['water_quality', 'air_quality', 'climate', 'urban_environment'],
                'strength': 9,
                'evidence_level': 'strong'
            }
        elif any(keyword in disease_lower for keyword in ['alimentare', 'listeria', 'epatite a']):
            correlation = {
                'potential': 'high',
                'factors': ['climate', 'water_quality', 'urban_environment'],
                'strength': 8,
                'evidence_level': 'strong'
            }
        elif any(keyword in disease_lower for keyword in ['malaria', 'leishmaniosi']):
            correlation = {
                'potential': 'high',
                'factors': ['climate', 'water_quality', 'urban_environment'],
                'strength': 9,
                'evidence_level': 'strong'
            }
        elif any(keyword in disease_lower for keyword in ['influenza', 'tubercolosi', 'covid']):
            correlation = {
                'potential': 'medium',
                'factors': ['air_quality', 'climate', 'urban_environment'],
                'strength': 6,
                'evidence_level': 'moderate'
            }
        elif any(keyword in disease_lower for keyword in ['morbillo', 'rosolia']):
            correlation = {
                'potential': 'medium',
                'factors': ['air_quality', 'urban_environment'],
                'strength': 5,
                'evidence_level': 'moderate'
            }
        else:
            correlation = {
                'potential': 'low',
                'factors': ['urban_environment'],
                'strength': 3,
                'evidence_level': 'weak'
            }
        
        return correlation
    
    def assess_data_quality(self, disease_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess data quality for environmental correlation analysis"""
        quality = {
            'score': 0,
            'temporal_coverage': 'unknown',
            'spatial_coverage': 'unknown',
            'sample_size': 'unknown',
            'suitability': 'unknown'
        }
        
        # Sample size assessment
        total_cases = disease_data.get('total_cases', 0)
        if total_cases >= 100:
            quality['sample_size'] = 'excellent'
            quality['score'] += 3
        elif total_cases >= 50:
            quality['sample_size'] = 'good'
            quality['score'] += 2
        elif total_cases >= 20:
            quality['sample_size'] = 'adequate'
            quality['score'] += 1
        else:
            quality['sample_size'] = 'limited'
        
        # Spatial coverage assessment
        municipalities = disease_data.get('municipalities_affected', 0)
        if municipalities >= 10:
            quality['spatial_coverage'] = 'excellent'
            quality['score'] += 3
        elif municipalities >= 5:
            quality['spatial_coverage'] = 'good'
            quality['score'] += 2
        elif municipalities >= 2:
            quality['spatial_coverage'] = 'adequate'
            quality['score'] += 1
        else:
            quality['spatial_coverage'] = 'limited'
        
        # Temporal coverage assessment
        if disease_data.get('first_case_date') and disease_data.get('last_case_date'):
            try:
                first_date = datetime.fromisoformat(disease_data['first_case_date'].replace('T', ' '))
                last_date = datetime.fromisoformat(disease_data['last_case_date'].replace('T', ' '))
                duration = (last_date - first_date).days
                
                if duration >= 365:
                    quality['temporal_coverage'] = 'excellent'
                    quality['score'] += 3
                elif duration >= 180:
                    quality['temporal_coverage'] = 'good'
                    quality['score'] += 2
                elif duration >= 90:
                    quality['temporal_coverage'] = 'adequate'
                    quality['score'] += 1
                else:
                    quality['temporal_coverage'] = 'limited'
            except:
                quality['temporal_coverage'] = 'unknown'
        
        # Overall suitability
        if quality['score'] >= 7:
            quality['suitability'] = 'excellent'
        elif quality['score'] >= 5:
            quality['suitability'] = 'good'
        elif quality['score'] >= 3:
            quality['suitability'] = 'adequate'
        else:
            quality['suitability'] = 'poor'
        
        return quality
    
    def assess_project_suitability(self, disease_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall suitability for environmental correlation project"""
        env_correlation = disease_data.get('environmental_correlation', {})
        data_quality = disease_data.get('data_quality', {})
        
        # Calculate weighted score
        env_score = env_correlation.get('strength', 0) * 0.4  # 40% weight for environmental potential
        data_score = data_quality.get('score', 0) * 0.6      # 60% weight for data quality
        
        total_score = env_score + data_score
        
        if total_score >= 8:
            recommendation = 'highly_recommended'
            priority = 'high'
        elif total_score >= 6:
            recommendation = 'recommended'
            priority = 'medium'
        elif total_score >= 4:
            recommendation = 'consider'
            priority = 'low'
        else:
            recommendation = 'not_recommended'
            priority = 'none'
        
        return {
            'score': round(total_score, 2),
            'recommendation': recommendation,
            'priority': priority,
            'reasoning': self.generate_recommendation_reasoning(env_correlation, data_quality)
        }
    
    def generate_recommendation_reasoning(self, env_correlation: Dict, data_quality: Dict) -> str:
        """Generate reasoning for project recommendation"""
        reasons = []
        
        # Environmental potential reasons
        if env_correlation.get('potential') == 'high':
            reasons.append("strong environmental correlation potential")
        elif env_correlation.get('potential') == 'medium':
            reasons.append("moderate environmental correlation potential")
        else:
            reasons.append("limited environmental correlation evidence")
        
        # Data quality reasons
        if data_quality.get('suitability') == 'excellent':
            reasons.append("excellent data quality and coverage")
        elif data_quality.get('suitability') == 'good':
            reasons.append("good data quality and coverage")
        elif data_quality.get('suitability') == 'adequate':
            reasons.append("adequate data for analysis")
        else:
            reasons.append("limited data quality")
        
        return "; ".join(reasons)
    
    def extract_disease_from_table_name(self, table_name: str) -> str:
        """Extract disease name from table name"""
        # Common patterns in table names
        disease_mappings = {
            'covid': 'COVID-19',
            'hiv': 'HIV/AIDS', 
            'legionellosi': 'Legionellosi',
            'morbillo': 'Morbillo/Rosolia',
            'influenza': 'Influenza',
            'tubercolosi': 'Tubercolosi',
            'malaria': 'Malaria',
            'listeria': 'Listeriosi',
            'epatite': 'Epatite',
            'meningite': 'Meningite',
            'tetano': 'Tetano',
            'creutzfeldt': 'Creutzfeldt-Jakob',
            'tossinfezioni': 'Tossinfezioni Alimentari',
            'leishmaniosi': 'Leishmaniosi',
            'trasmissione_sessuale': 'Malattie Trasmissione Sessuale'
        }
        
        table_lower = table_name.lower()
        for key, disease in disease_mappings.items():
            if key in table_lower:
                return disease
        
        return table_name.replace('gesan_malattie_infettive_', '').replace('ie_', '').replace('_', ' ').title()
    
    def assess_table_environmental_potential(self, table_name: str) -> str:
        """Assess environmental correlation potential for a specialized table"""
        table_lower = table_name.lower()
        
        high_potential = ['legionellosi', 'alimentari', 'listeria', 'malaria', 'leishmaniosi', 'epatite']
        medium_potential = ['covid', 'influenza', 'tubercolosi', 'morbillo']
        
        for keyword in high_potential:
            if keyword in table_lower:
                return 'high'
        
        for keyword in medium_potential:
            if keyword in table_lower:
                return 'medium'
        
        return 'low'
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        print("\n📊 Generating comprehensive analysis report...")
        
        # Get all disease data
        surveillance_diseases = self.get_all_diseases_list()
        specialized_tables = self.get_specialized_diseases_tables()
        
        # Categorize diseases for project suitability
        highly_recommended = [d for d in surveillance_diseases if d.get('project_suitability', {}).get('recommendation') == 'highly_recommended']
        recommended = [d for d in surveillance_diseases if d.get('project_suitability', {}).get('recommendation') == 'recommended']
        consider = [d for d in surveillance_diseases if d.get('project_suitability', {}).get('recommendation') == 'consider']
        
        report = {
            'analysis_date': datetime.now().isoformat(),
            'database_summary': {
                'total_diseases_surveillance': len(surveillance_diseases),
                'specialized_tables': len(specialized_tables),
                'total_cases': sum(d.get('total_cases', 0) for d in surveillance_diseases)
            },
            'project_recommendations': {
                'highly_recommended': highly_recommended,
                'recommended': recommended,
                'consider': consider,
                'counts': {
                    'highly_recommended': len(highly_recommended),
                    'recommended': len(recommended),
                    'consider': len(consider)
                }
            },
            'environmental_factors_available': self.environmental_factors,
            'all_diseases': surveillance_diseases,
            'specialized_tables': specialized_tables
        }
        
        return report
    
    def print_summary_report(self, report: Dict[str, Any]):
        """Print formatted summary report"""
        print("\n" + "="*80)
        print("🦠 HEALTHTRACE - INFECTIOUS DISEASES & ENVIRONMENTAL ANALYSIS")
        print("="*80)
        
        print(f"\n📊 DATABASE SUMMARY:")
        print(f"   • Total diseases in surveillance system: {report['database_summary']['total_diseases_surveillance']}")
        print(f"   • Specialized investigation tables: {report['database_summary']['specialized_tables']}")
        print(f"   • Total cases across all diseases: {report['database_summary']['total_cases']:,}")
        
        print(f"\n🎯 PROJECT SUITABILITY RECOMMENDATIONS:")
        
        # Highly recommended diseases
        highly_rec = report['project_recommendations']['highly_recommended']
        print(f"\n🥇 HIGHLY RECOMMENDED ({len(highly_rec)} diseases):")
        for disease in highly_rec:
            env_factors = ", ".join(disease['environmental_correlation']['factors'])
            print(f"   • {disease['malattia_segnalata']}")
            print(f"     - Cases: {disease['total_cases']:,}")
            print(f"     - Environmental factors: {env_factors}")
            print(f"     - Score: {disease['project_suitability']['score']}/10")
            print(f"     - Reasoning: {disease['project_suitability']['reasoning']}")
        
        # Recommended diseases
        rec = report['project_recommendations']['recommended']
        print(f"\n🥈 RECOMMENDED ({len(rec)} diseases):")
        for disease in rec:
            env_factors = ", ".join(disease['environmental_correlation']['factors'])
            print(f"   • {disease['malattia_segnalata']}")
            print(f"     - Cases: {disease['total_cases']:,}")
            print(f"     - Environmental factors: {env_factors}")
            print(f"     - Score: {disease['project_suitability']['score']}/10")
        
        # Consider diseases
        consider = report['project_recommendations']['consider']
        if consider:
            print(f"\n🥉 CONSIDER ({len(consider)} diseases):")
            for disease in consider[:5]:  # Show top 5 only
                print(f"   • {disease['malattia_segnalata']} - Cases: {disease['total_cases']:,}")
        
        print(f"\n🌍 ENVIRONMENTAL FACTORS AVAILABLE FOR CORRELATION:")
        for category, factors in report['environmental_factors_available'].items():
            print(f"   • {category.replace('_', ' ').title()}: {', '.join(factors)}")
        
        print(f"\n✅ ANALYSIS COMPLETE - Report generated at {report['analysis_date']}")

def main():
    """Main analysis function"""
    print("🚀 Starting HealthTrace Environmental Correlation Analysis...")
    
    analyzer = EnvironmentalCorrelationAnalyzer()
    
    # Connect to database
    if not analyzer.connect_database():
        print("❌ Cannot proceed without database connection")
        return
    
    try:
        # Generate comprehensive report
        report = analyzer.generate_comprehensive_report()
        
        # Print summary
        analyzer.print_summary_report(report)
        
        # Save detailed report to file
        output_file = '/home/amir/Documents/amir/Ambientale/HealthTrace/environmental_correlation_analysis_report.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Detailed report saved to: {output_file}")
        
        # Create markdown summary
        markdown_file = '/home/amir/Documents/amir/Ambientale/HealthTrace/diseases_environmental_analysis_summary.md'
        create_markdown_summary(report, markdown_file)
        print(f"📝 Markdown summary saved to: {markdown_file}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        analyzer.db.disconnect()

def create_markdown_summary(report: Dict[str, Any], filename: str):
    """Create markdown summary of the analysis"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# 🦠 HealthTrace - Diseases & Environmental Factors Analysis\n\n")
        f.write(f"**Analysis Date:** {report['analysis_date']}\n\n")
        
        f.write("## 📊 Database Summary\n\n")
        f.write(f"- **Total diseases in surveillance:** {report['database_summary']['total_diseases_surveillance']}\n")
        f.write(f"- **Specialized investigation tables:** {report['database_summary']['specialized_tables']}\n")  
        f.write(f"- **Total cases across all diseases:** {report['database_summary']['total_cases']:,}\n\n")
        
        f.write("## 🎯 Project Recommendations\n\n")
        
        # Highly recommended
        highly_rec = report['project_recommendations']['highly_recommended']
        f.write(f"### 🥇 Highly Recommended Diseases ({len(highly_rec)})\n\n")
        for disease in highly_rec:
            f.write(f"#### {disease['malattia_segnalata']}\n")
            f.write(f"- **Cases:** {disease['total_cases']:,}\n")
            f.write(f"- **Environmental Correlation:** {disease['environmental_correlation']['potential']} ({disease['environmental_correlation']['strength']}/10)\n")
            f.write(f"- **Environmental Factors:** {', '.join(disease['environmental_correlation']['factors'])}\n")
            f.write(f"- **Data Quality:** {disease['data_quality']['suitability']}\n")
            f.write(f"- **Project Score:** {disease['project_suitability']['score']}/10\n")
            f.write(f"- **Reasoning:** {disease['project_suitability']['reasoning']}\n\n")
        
        # Recommended
        rec = report['project_recommendations']['recommended']
        if rec:
            f.write(f"### 🥈 Recommended Diseases ({len(rec)})\n\n")
            for disease in rec:
                f.write(f"- **{disease['malattia_segnalata']}** - {disease['total_cases']:,} cases (Score: {disease['project_suitability']['score']}/10)\n")
        
        f.write("\n## 🌍 Available Environmental Factors\n\n")
        for category, factors in report['environmental_factors_available'].items():
            f.write(f"- **{category.replace('_', ' ').title()}:** {', '.join(factors)}\n")

if __name__ == "__main__":
    main()
