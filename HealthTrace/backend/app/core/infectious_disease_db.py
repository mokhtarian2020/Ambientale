"""
Real Infectious Disease Database Integration
Connects HealthTrace to the real GESAN malattie infettive database
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class InfectiousDiseaseDB:
    """
    Connection manager for real infectious disease database
    Server: 10.10.13.11:5432
    Database: gesan_malattieinfettive
    """
    
    def __init__(self):
        # Real database connection
        self.database_url = "postgresql://postgres:postgres@10.10.13.11:5432/gesan_malattieinfettive"
        
        try:
            self.engine = create_engine(
                self.database_url,
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle connections every hour
                connect_args={
                    "connect_timeout": 10,
                    "options": "-c timezone=Europe/Rome"  # Italian timezone
                }
            )
            
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Test connection
            self._test_connection()
            logger.info("✅ Connected to real infectious disease database")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to infectious disease database: {e}")
            self.engine = None
            self.SessionLocal = None
    
    def _test_connection(self):
        """Test database connection and log basic info"""
        try:
            with self.engine.connect() as conn:
                # Test basic connectivity
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"Database version: {version}")
                
                # List available tables
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
                
                tables = [row[0] for row in result.fetchall()]
                logger.info(f"Available tables: {tables}")
                
                return True
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            raise
    
    def get_session(self):
        """Get database session"""
        if not self.SessionLocal:
            raise Exception("Database connection not available")
        return self.SessionLocal()
    
    def explore_database_schema(self) -> Dict[str, Any]:
        """
        Explore the database schema to understand table structure
        This helps us map the real data to HealthTrace models
        """
        try:
            with self.engine.connect() as conn:
                # Get table information
                tables_query = text("""
                    SELECT 
                        t.table_name,
                        t.table_type,
                        obj_description(c.oid, 'pg_class') as table_comment
                    FROM information_schema.tables t
                    LEFT JOIN pg_class c ON c.relname = t.table_name
                    WHERE t.table_schema = 'public'
                    ORDER BY t.table_name
                """)
                
                result = conn.execute(tables_query)
                tables_info = []
                
                for row in result.fetchall():
                    table_name = row[0]
                    
                    # Get column information for each table
                    columns_query = text("""
                        SELECT 
                            column_name,
                            data_type,
                            is_nullable,
                            column_default,
                            character_maximum_length
                        FROM information_schema.columns
                        WHERE table_name = :table_name
                        AND table_schema = 'public'
                        ORDER BY ordinal_position
                    """)
                    
                    columns_result = conn.execute(columns_query, {"table_name": table_name})
                    columns = []
                    
                    for col_row in columns_result.fetchall():
                        columns.append({
                            "name": col_row[0],
                            "type": col_row[1],
                            "nullable": col_row[2] == "YES",
                            "default": col_row[3],
                            "max_length": col_row[4]
                        })
                    
                    # Get row count
                    count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                    try:
                        count_result = conn.execute(count_query)
                        row_count = count_result.fetchone()[0]
                    except Exception:
                        row_count = "Unknown"
                    
                    tables_info.append({
                        "table_name": table_name,
                        "table_type": row[1],
                        "comment": row[2],
                        "row_count": row_count,
                        "columns": columns
                    })
                
                return {
                    "database_name": "gesan_malattieinfettive",
                    "server": "10.10.13.11:5432",
                    "total_tables": len(tables_info),
                    "tables": tables_info
                }
                
        except Exception as e:
            logger.error(f"Schema exploration failed: {e}")
            return {"error": str(e)}
    
    def query_disease_cases(self, 
                          disease_type: str = None,
                          start_date: str = None,
                          end_date: str = None,
                          istat_code: str = None,
                          limit: int = 1000) -> pd.DataFrame:
        """
        Query disease cases from real database
        
        Args:
            disease_type: Type of disease (influenza, legionellosis, hepatitis_a)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)  
            istat_code: ISTAT geographic code
            limit: Maximum number of records
        
        Returns:
            DataFrame with disease cases
        """
        try:
            # This query will need to be adapted based on actual table structure
            # We'll start with a generic approach and refine based on schema exploration
            
            base_query = """
                SELECT *
                FROM malattie_infettive 
                WHERE 1=1
            """
            
            params = {}
            
            if disease_type:
                base_query += " AND LOWER(malattia) LIKE LOWER(:disease_type)"
                params["disease_type"] = f"%{disease_type}%"
            
            if start_date:
                base_query += " AND data_diagnosi >= :start_date"
                params["start_date"] = start_date
                
            if end_date:
                base_query += " AND data_diagnosi <= :end_date"
                params["end_date"] = end_date
                
            if istat_code:
                base_query += " AND codice_istat = :istat_code"
                params["istat_code"] = istat_code
            
            base_query += f" ORDER BY data_diagnosi DESC LIMIT {limit}"
            
            with self.engine.connect() as conn:
                result = conn.execute(text(base_query), params)
                columns = result.keys()
                data = result.fetchall()
                
                df = pd.DataFrame(data, columns=columns)
                logger.info(f"Retrieved {len(df)} disease cases from real database")
                
                return df
                
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return pd.DataFrame()
    
    def get_disease_statistics(self) -> Dict[str, Any]:
        """
        Get basic statistics from the real database
        """
        try:
            with self.engine.connect() as conn:
                # This will be refined based on actual schema
                stats_queries = {
                    "total_cases": "SELECT COUNT(*) FROM malattie_infettive",
                    "recent_cases": """
                        SELECT COUNT(*) FROM malattie_infettive 
                        WHERE data_diagnosi >= CURRENT_DATE - INTERVAL '30 days'
                    """,
                    "diseases_by_type": """
                        SELECT malattia, COUNT(*) as count
                        FROM malattie_infettive 
                        GROUP BY malattia 
                        ORDER BY count DESC
                    """,
                    "cases_by_region": """
                        SELECT regione, COUNT(*) as count
                        FROM malattie_infettive 
                        GROUP BY regione 
                        ORDER BY count DESC
                    """
                }
                
                statistics = {}
                
                for stat_name, query in stats_queries.items():
                    try:
                        result = conn.execute(text(query))
                        if stat_name in ["total_cases", "recent_cases"]:
                            statistics[stat_name] = result.fetchone()[0]
                        else:
                            statistics[stat_name] = [
                                {"name": row[0], "count": row[1]} 
                                for row in result.fetchall()
                            ]
                    except Exception as e:
                        logger.warning(f"Query {stat_name} failed: {e}")
                        statistics[stat_name] = None
                
                return statistics
                
        except Exception as e:
            logger.error(f"Statistics query failed: {e}")
            return {"error": str(e)}
    
    def map_to_healthtrace_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Map real database format to HealthTrace expected format
        This will need to be customized based on actual schema
        """
        try:
            # Standard mapping - will be refined based on real schema
            mapped_df = df.copy()
            
            # Common column mappings (adjust based on real schema)
            column_mappings = {
                'data_diagnosi': 'diagnosis_date',
                'malattia': 'disease_name', 
                'codice_istat': 'istat_code',
                'comune': 'municipality',
                'provincia': 'province',
                'regione': 'region',
                'eta': 'age',
                'sesso': 'gender'
            }
            
            # Apply mappings if columns exist
            for old_col, new_col in column_mappings.items():
                if old_col in mapped_df.columns:
                    mapped_df = mapped_df.rename(columns={old_col: new_col})
            
            # Add standardized disease categories for HealthTrace
            if 'disease_name' in mapped_df.columns:
                mapped_df['healthtrace_disease_category'] = mapped_df['disease_name'].apply(
                    self._categorize_disease
                )
            
            logger.info(f"Mapped {len(mapped_df)} records to HealthTrace format")
            return mapped_df
            
        except Exception as e:
            logger.error(f"Mapping failed: {e}")
            return df
    
    def _categorize_disease(self, disease_name: str) -> str:
        """
        Map real disease names to HealthTrace categories
        """
        if not disease_name:
            return "unknown"
        
        disease_lower = disease_name.lower()
        
        # Influenza variants
        if any(keyword in disease_lower for keyword in ['influenza', 'flu', 'grippe']):
            return "influenza"
        
        # Legionellosis variants  
        if any(keyword in disease_lower for keyword in ['legionella', 'legionellosi']):
            return "legionellosis"
        
        # Hepatitis A variants
        if any(keyword in disease_lower for keyword in ['epatite a', 'hepatitis a', 'hep a']):
            return "hepatitis_a"
        
        return "other"

# Global instance
infectious_disease_db = InfectiousDiseaseDB()

def get_infectious_disease_db() -> InfectiousDiseaseDB:
    """Get the infectious disease database instance"""
    return infectious_disease_db
