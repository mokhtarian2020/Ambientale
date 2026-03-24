"""
Real GESAN Infectious Disease Database Connection Manager
Handles connections to the Italian health surveillance database
"""

import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InfectiousDiseaseDB:
    """Manager for GESAN infectious disease database connections"""
    
    def __init__(self):
        self.connection_params = {
            'host': '10.10.13.11',
            'port': 5432,
            'database': 'gesan_malattieinfettive',
            'user': 'postgres',
            'password': 'postgres',
            'connect_timeout': 10
        }
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.set_session(autocommit=True)
            logger.info("✅ Connected to GESAN infectious disease database")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("🔌 Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query, params)
            
            if cursor.description:
                results = cursor.fetchall()
                # Convert RealDictRow to regular dict and handle datetime serialization
                processed_results = []
                for row in results:
                    row_dict = dict(row)
                    for key, value in row_dict.items():
                        if isinstance(value, datetime):
                            row_dict[key] = value.isoformat()
                    processed_results.append(row_dict)
                return processed_results
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ Query execution error: {str(e)}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def get_database_summary(self) -> Dict[str, Any]:
        """Get overview of the database structure"""
        summary = {
            "database_info": {},
            "table_stats": [],
            "key_tables": []
        }
        
        # Get PostgreSQL version and basic info
        version_query = "SELECT version() as version"
        version_result = self.execute_query(version_query)
        if version_result:
            summary["database_info"]["version"] = version_result[0]["version"]
        
        # Get table statistics
        tables_query = """
            SELECT 
                t.table_name,
                (SELECT COUNT(*) FROM information_schema.columns 
                 WHERE table_name = t.table_name AND table_schema = 'public') as column_count
            FROM information_schema.tables t
            WHERE t.table_schema = 'public' 
            AND t.table_type = 'BASE TABLE'
            AND t.table_name LIKE '%malattie_infettive%'
            ORDER BY t.table_name
        """
        
        table_results = self.execute_query(tables_query)
        
        # Get row counts for each table
        for table in table_results:
            try:
                count_query = f'SELECT COUNT(*) as row_count FROM "{table["table_name"]}"'
                count_result = self.execute_query(count_query)
                table["row_count"] = count_result[0]["row_count"] if count_result else 0
            except:
                table["row_count"] = 0
        
        summary["table_stats"] = table_results
        
        # Identify key tables with data
        summary["key_tables"] = [
            table for table in table_results 
            if table["row_count"] > 0
        ]
        
        return summary
    
    def get_recent_cases(self, limit: int = 50, days_back: int = 30) -> List[Dict[str, Any]]:
        """Get recent infectious disease cases"""
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        query = """
            SELECT 
                s.id,
                s.malattia_segnalata,
                s.data_inizio_sintomi,
                s.data_segnalazione,
                s.comune_residenza_codice_istat,
                s.stato_attuale,
                s.professione,
                s.descrizione_sintomi,
                s.codice_icdix
            FROM gesan_malattie_infettive_segnalazione s
            WHERE s.data_segnalazione >= %s
            ORDER BY s.data_segnalazione DESC
            LIMIT %s
        """
        
        return self.execute_query(query, (cutoff_date, limit))
    
    def get_covid_cases(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get COVID-19 specific case data"""
        query = """
            SELECT 
                c.id,
                c.tipo_caso,
                c.data_insorgenza_sintomi,
                c.tipo_sintomi,
                c.febbre,
                c.tosse,
                c.difficolta_respiratoria,
                c.operatore_sanitario,
                c.followup_esito,
                c.vaccino_covid,
                c.vaccino_covid_numero_dosi
            FROM gesan_malattie_infettive_ie_covid c
            ORDER BY c.data_insorgenza_sintomi DESC
            LIMIT %s
        """
        
        return self.execute_query(query, (limit,))
    
    def get_disease_statistics(self) -> Dict[str, Any]:
        """Get disease statistics and trends"""
        stats = {}
        
        # Overall case counts by disease type
        disease_counts_query = """
            SELECT 
                malattia_segnalata,
                COUNT(*) as case_count,
                MAX(data_segnalazione) as latest_case
            FROM gesan_malattie_infettive_segnalazione
            GROUP BY malattia_segnalata
            ORDER BY case_count DESC
        """
        
        stats["disease_counts"] = self.execute_query(disease_counts_query)
        
        # Monthly trends for recent period
        monthly_trends_query = """
            SELECT 
                DATE_TRUNC('month', data_segnalazione) as month,
                COUNT(*) as cases
            FROM gesan_malattie_infettive_segnalazione
            WHERE data_segnalazione >= CURRENT_DATE - INTERVAL '12 months'
            GROUP BY DATE_TRUNC('month', data_segnalazione)
            ORDER BY month
        """
        
        stats["monthly_trends"] = self.execute_query(monthly_trends_query)
        
        # Geographic distribution (by ISTAT codes)
        geographic_query = """
            SELECT 
                comune_residenza_codice_istat,
                COUNT(*) as case_count
            FROM gesan_malattie_infettive_segnalazione
            WHERE comune_residenza_codice_istat IS NOT NULL 
            AND comune_residenza_codice_istat != ''
            GROUP BY comune_residenza_codice_istat
            ORDER BY case_count DESC
            LIMIT 20
        """
        
        stats["geographic_distribution"] = self.execute_query(geographic_query)
        
        return stats
    
    def get_contact_tracing_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get contact tracing information"""
        query = """
            SELECT 
                lc.id,
                lc.id_indagine_epidemilogica,
                lc.nome,
                lc.cognome,
                lc.comune,
                lc.indirizzo,
                lc.telefono,
                lc.create_date
            FROM gesan_malattie_infettive_ie_lista_contatti lc
            ORDER BY lc.create_date DESC
            LIMIT %s
        """
        
        return self.execute_query(query, (limit,))
    
    def get_symptoms_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get symptoms reporting data"""
        query = """
            SELECT 
                s.id,
                s.id_indagine_epidemiologica,
                s.sintomo,
                s.data_dal,
                s.data_al,
                s.create_date
            FROM gesan_malattie_infettive_ie_sintomatologia s
            ORDER BY s.create_date DESC
            LIMIT %s
        """
        
        return self.execute_query(query, (limit,))
    
    def search_cases_by_municipality(self, istat_code: str) -> List[Dict[str, Any]]:
        """Search cases by municipality ISTAT code"""
        query = """
            SELECT 
                s.id,
                s.malattia_segnalata,
                s.data_inizio_sintomi,
                s.data_segnalazione,
                s.stato_attuale,
                s.descrizione_sintomi
            FROM gesan_malattie_infettive_segnalazione s
            WHERE s.comune_residenza_codice_istat = %s
            ORDER BY s.data_segnalazione DESC
        """
        
        return self.execute_query(query, (istat_code,))

# Global database instance
db_manager = InfectiousDiseaseDB()
