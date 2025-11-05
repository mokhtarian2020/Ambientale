"""
Data Pipeline Architecture for HealthTrace 3-Disease Project
Implements the specified data flow:
File Upload → Data Warehouse → Kafka Broker → Algorithm Processing → API Endpoints

Handles batch import of environmental and health data from Italian sources:
- ARPA Campania (air quality)
- ISPRA (environmental indicators)
- ISTAT (statistical data)
- Regional health authorities (disease data)
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import logging
from pathlib import Path
import asyncio
from dataclasses import dataclass
import hashlib

# FastAPI and database
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# Kafka
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

# Database models
from app.models.environmental import EnvironmentalData
from app.models.climate import ClimateData
from app.models.target_diseases import InfluenzaCase, LegionellosisCase, HepatitisACase
from app.core.database import get_db

# Analytics
from analytics.advanced_models import ComprehensiveAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FileProcessingResult:
    """Result of file processing operation"""
    success: bool
    records_processed: int
    errors: List[str]
    file_hash: str
    processing_time: float
    data_type: str


class DataWarehouseManager:
    """
    Manages data warehouse operations for environmental and health data
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.supported_formats = ['.csv', '.xlsx', '.json', '.xml']
        
    def validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file format and size"""
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.supported_formats:
            raise HTTPException(400, f"Unsupported file format: {file_ext}")
        
        # Check file size (max 100MB)
        if file.size > 100 * 1024 * 1024:
            raise HTTPException(400, "File too large (max 100MB)")
        
        return True
    
    def detect_data_type(self, df: pd.DataFrame, filename: str) -> str:
        """Detect the type of data based on column names and filename"""
        
        filename_lower = filename.lower()
        columns = [col.lower() for col in df.columns]
        
        # Environmental/Air Quality Data (ARPA Campania format)
        if any(pollutant in columns for pollutant in ['pm10', 'pm25', 'pm2.5', 'o3', 'no2', 'so2', 'co', 'c6h6']):
            return "environmental"
        
        # Climate/Weather Data
        if any(climate in columns for climate in ['temperatura', 'temperature', 'umidita', 'humidity', 'precipitazione', 'precipitation']):
            return "climate"
        
        # Water Quality Data
        if any(water in columns for water in ['ph', 'e.coli', 'ecoli', 'conta di escherichia']):
            return "water_quality"
        
        # Disease/Health Data
        if any(health in columns for health in ['caso', 'case', 'malattia', 'disease', 'sintomi', 'symptoms']):
            return "health"
        
        # Filename-based detection
        if any(keyword in filename_lower for keyword in ['rqa', 'qualita', 'aria', 'air']):
            return "environmental"
        elif any(keyword in filename_lower for keyword in ['meteo', 'clima', 'weather']):
            return "climate"
        elif any(keyword in filename_lower for keyword in ['acqua', 'water']):
            return "water_quality"
        elif any(keyword in filename_lower for keyword in ['salute', 'health', 'malattia', 'disease']):
            return "health"
        
        return "unknown"
    
    def normalize_arpa_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize ARPA Campania data format to our schema"""
        
        # Expected ARPA columns: _id, Stazione, Descrizione, Latitude, Longitude, Inquinante, ISTAT Code, Data_ora, Valore, Um
        column_mapping = {
            '_id': 'record_id',
            'stazione': 'station_code',
            'descrizione': 'station_name',
            'latitude': 'latitude',
            'longitude': 'longitude',
            'inquinante': 'pollutant_type',
            'istat code': 'istat_code',
            'data_ora': 'measurement_datetime',
            'valore': 'value',
            'um': 'unit'
        }
        
        # Normalize column names
        df_normalized = df.copy()
        df_normalized.columns = [col.lower().strip() for col in df_normalized.columns]
        
        # Apply column mapping
        for old_col, new_col in column_mapping.items():
            if old_col in df_normalized.columns:
                df_normalized = df_normalized.rename(columns={old_col: new_col})
        
        # Parse datetime
        if 'measurement_datetime' in df_normalized.columns:
            df_normalized['measurement_datetime'] = pd.to_datetime(df_normalized['measurement_datetime'], errors='coerce')
            df_normalized['measurement_date'] = df_normalized['measurement_datetime'].dt.date
            df_normalized['measurement_year'] = df_normalized['measurement_datetime'].dt.year
            df_normalized['measurement_month'] = df_normalized['measurement_datetime'].dt.month
            df_normalized['measurement_hour'] = df_normalized['measurement_datetime'].dt.hour
        
        # Handle missing values
        if 'value' in df_normalized.columns:
            # ARPA uses -9999 for missing values
            df_normalized['value'] = pd.to_numeric(df_normalized['value'], errors='coerce')
            df_normalized.loc[df_normalized['value'] == -9999, 'value'] = np.nan
        
        return df_normalized
    
    def pivot_environmental_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Pivot environmental data from long to wide format"""
        
        if 'pollutant_type' not in df.columns:
            return df
        
        # Define pollutant mapping
        pollutant_mapping = {
            'PM10': 'pm10',
            'PM2,5': 'pm25',
            'PM2.5': 'pm25',
            'O3': 'ozone',
            'NO2': 'no2',
            'SO2': 'so2',
            'C6H6': 'benzene',
            'CO': 'co',
            'As in PM10': 'arsenic'
        }
        
        # Map pollutant names
        df['pollutant_normalized'] = df['pollutant_type'].map(pollutant_mapping)
        df = df.dropna(subset=['pollutant_normalized'])
        
        # Pivot data
        pivot_df = df.pivot_table(
            index=['istat_code', 'station_code', 'measurement_date', 'measurement_year', 'measurement_month'],
            columns='pollutant_normalized',
            values='value',
            aggfunc='mean'  # Average if multiple readings per day
        ).reset_index()
        
        # Flatten column names
        pivot_df.columns.name = None
        
        return pivot_df
    
    def save_environmental_data(self, df: pd.DataFrame) -> int:
        """Save environmental data to data warehouse"""
        
        records_saved = 0
        
        for _, row in df.iterrows():
            try:
                env_record = EnvironmentalData(
                    istat_code=str(row.get('istat_code', '')),
                    station_code=str(row.get('station_code', '')),
                    station_name=str(row.get('station_name', '')),
                    latitude=float(row.get('latitude')) if pd.notna(row.get('latitude')) else None,
                    longitude=float(row.get('longitude')) if pd.notna(row.get('longitude')) else None,
                    measurement_date=row.get('measurement_date'),
                    measurement_year=int(row.get('measurement_year')) if pd.notna(row.get('measurement_year')) else None,
                    measurement_month=int(row.get('measurement_month')) if pd.notna(row.get('measurement_month')) else None,
                    pm10=float(row.get('pm10')) if pd.notna(row.get('pm10')) else None,
                    pm25=float(row.get('pm25')) if pd.notna(row.get('pm25')) else None,
                    ozone=float(row.get('ozone')) if pd.notna(row.get('ozone')) else None,
                    no2=float(row.get('no2')) if pd.notna(row.get('no2')) else None,
                    so2=float(row.get('so2')) if pd.notna(row.get('so2')) else None,
                    benzene=float(row.get('benzene')) if pd.notna(row.get('benzene')) else None,
                    co=float(row.get('co')) if pd.notna(row.get('co')) else None,
                    arsenic=float(row.get('arsenic')) if pd.notna(row.get('arsenic')) else None,
                    data_source="file_upload",
                    validation_status="pending"
                )
                
                self.db.add(env_record)
                records_saved += 1
                
            except Exception as e:
                logger.error(f"Error saving environmental record: {str(e)}")
                continue
        
        self.db.commit()
        return records_saved
    
    def save_climate_data(self, df: pd.DataFrame) -> int:
        """Save climate data to data warehouse"""
        
        records_saved = 0
        
        # Normalize climate column names
        climate_mapping = {
            'temperatura': 'temperature_avg',
            'temperature': 'temperature_avg',
            'temperatura aria - min': 'temperature_min',
            'temperatura aria - max': 'temperature_max',
            'umidita': 'humidity',
            'humidity': 'humidity',
            'umidità aria - grezzo': 'humidity',
            'precipitazione': 'precipitation',
            'precipitation': 'precipitation',
            'precipitazione - grezzo': 'precipitation',
            'velocita vento': 'wind_speed',
            'wind_speed': 'wind_speed',
            'direzione vento': 'wind_direction',
            'wind_direction': 'wind_direction'
        }
        
        # Rename columns
        df_climate = df.copy()
        df_climate.columns = [col.lower().strip() for col in df_climate.columns]
        
        for old_col, new_col in climate_mapping.items():
            if old_col in df_climate.columns:
                df_climate = df_climate.rename(columns={old_col: new_col})
        
        for _, row in df_climate.iterrows():
            try:
                climate_record = ClimateData(
                    istat_code=str(row.get('istat_code', '')),
                    station_code=str(row.get('station_code', '')),
                    measurement_date=row.get('data', row.get('date', row.get('measurement_date'))),
                    measurement_year=int(row.get('measurement_year', datetime.now().year)),
                    measurement_month=int(row.get('measurement_month', 1)),
                    measurement_day=int(row.get('measurement_day', 1)),
                    temperature_avg=float(row.get('temperature_avg')) if pd.notna(row.get('temperature_avg')) else None,
                    temperature_min=float(row.get('temperature_min')) if pd.notna(row.get('temperature_min')) else None,
                    temperature_max=float(row.get('temperature_max')) if pd.notna(row.get('temperature_max')) else None,
                    humidity=float(row.get('humidity')) if pd.notna(row.get('humidity')) else None,
                    precipitation=float(row.get('precipitation')) if pd.notna(row.get('precipitation')) else None,
                    wind_speed=float(row.get('wind_speed')) if pd.notna(row.get('wind_speed')) else None,
                    wind_direction=float(row.get('wind_direction')) if pd.notna(row.get('wind_direction')) else None,
                    data_source="file_upload",
                    validation_status="pending"
                )
                
                self.db.add(climate_record)
                records_saved += 1
                
            except Exception as e:
                logger.error(f"Error saving climate record: {str(e)}")
                continue
        
        self.db.commit()
        return records_saved
    
    def process_file(self, file: UploadFile) -> FileProcessingResult:
        """Process uploaded file and save to data warehouse"""
        
        start_time = datetime.now()
        errors = []
        
        try:
            # Validate file
            self.validate_file(file)
            
            # Read file content
            content = file.file.read()
            file_hash = hashlib.md5(content).hexdigest()
            
            # Parse based on file type
            file_ext = Path(file.filename).suffix.lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(pd.io.common.BytesIO(content))
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(pd.io.common.BytesIO(content))
            elif file_ext == '.json':
                data = json.loads(content.decode('utf-8'))
                df = pd.json_normalize(data) if isinstance(data, list) else pd.DataFrame([data])
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Detect data type
            data_type = self.detect_data_type(df, file.filename)
            
            # Process based on data type
            if data_type == "environmental":
                df_normalized = self.normalize_arpa_data(df)
                df_pivoted = self.pivot_environmental_data(df_normalized)
                records_saved = self.save_environmental_data(df_pivoted)
                
            elif data_type == "climate":
                records_saved = self.save_climate_data(df)
                
            else:
                # For now, just log unknown data types
                logger.warning(f"Unknown data type: {data_type} for file: {file.filename}")
                records_saved = 0
                errors.append(f"Unknown data type: {data_type}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return FileProcessingResult(
                success=True,
                records_processed=records_saved,
                errors=errors,
                file_hash=file_hash,
                processing_time=processing_time,
                data_type=data_type
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"File processing failed: {str(e)}"
            logger.error(error_msg)
            
            return FileProcessingResult(
                success=False,
                records_processed=0,
                errors=[error_msg],
                file_hash="",
                processing_time=processing_time,
                data_type="unknown"
            )


class KafkaDataStreamer:
    """
    Manages Kafka streaming for real-time data processing
    """
    
    def __init__(self, kafka_servers: List[str] = None):
        self.kafka_servers = kafka_servers or ['localhost:9092']
        self.producer = None
        self.consumer = None
        
    def get_producer(self) -> KafkaProducer:
        """Get or create Kafka producer"""
        if self.producer is None:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8') if k else None
            )
        return self.producer
    
    def send_to_analytics_queue(self, data: Dict[str, Any], topic: str = "environmental_data"):
        """Send data to Kafka for analytics processing"""
        
        try:
            producer = self.get_producer()
            
            # Add metadata
            message = {
                'timestamp': datetime.now().isoformat(),
                'data_type': data.get('data_type', 'unknown'),
                'data': data
            }
            
            # Send to Kafka
            future = producer.send(topic, value=message)
            result = future.get(timeout=10)
            
            logger.info(f"Sent message to Kafka topic {topic}: {result}")
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending to Kafka: {str(e)}")
            return False
    
    def consume_analytics_queue(self, topic: str = "environmental_data"):
        """Consume messages from Kafka for analytics processing"""
        
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.kafka_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='analytics_processor',
            auto_offset_reset='latest'
        )
        
        for message in consumer:
            try:
                data = message.value
                self.process_analytics_message(data)
            except Exception as e:
                logger.error(f"Error processing Kafka message: {str(e)}")
    
    def process_analytics_message(self, message: Dict[str, Any]):
        """Process analytics message from Kafka"""
        
        data_type = message.get('data_type')
        data = message.get('data')
        
        if data_type == 'environmental':
            # Trigger environmental analytics
            self.trigger_environmental_analytics(data)
        elif data_type == 'climate':
            # Trigger climate analytics
            self.trigger_climate_analytics(data)
        elif data_type == 'health':
            # Trigger health correlation analytics
            self.trigger_health_analytics(data)
    
    def trigger_environmental_analytics(self, data: Dict[str, Any]):
        """Trigger environmental analytics processing"""
        
        try:
            # Create analyzer for each disease
            diseases = ['influenza', 'legionellosis', 'hepatitis_a']
            
            for disease in diseases:
                analyzer = ComprehensiveAnalyzer(disease)
                
                # For real implementation, fetch data from database
                # Here we simulate with the received data
                sample_df = pd.DataFrame([data])
                
                if not sample_df.empty:
                    results = analyzer.run_all_analyses(sample_df)
                    logger.info(f"Analytics completed for {disease}: {len(results)} models")
                    
        except Exception as e:
            logger.error(f"Error in environmental analytics: {str(e)}")
    
    def trigger_climate_analytics(self, data: Dict[str, Any]):
        """Trigger climate analytics processing"""
        logger.info("Climate analytics triggered")
        # Implement climate-specific analytics
    
    def trigger_health_analytics(self, data: Dict[str, Any]):
        """Trigger health correlation analytics"""
        logger.info("Health correlation analytics triggered")
        # Implement health correlation analytics


class DataPipelineOrchestrator:
    """
    Main orchestrator for the data pipeline
    File Upload → Data Warehouse → Kafka → Analytics → API
    """
    
    def __init__(self, db_session: Session):
        self.dwh_manager = DataWarehouseManager(db_session)
        self.kafka_streamer = KafkaDataStreamer()
        
    async def process_file_upload(self, file: UploadFile) -> FileProcessingResult:
        """Main entry point for file processing"""
        
        logger.info(f"Processing file upload: {file.filename}")
        
        # Step 1: Process file and save to Data Warehouse
        result = self.dwh_manager.process_file(file)
        
        if result.success:
            # Step 2: Send notification to Kafka for analytics processing
            kafka_message = {
                'data_type': result.data_type,
                'records_processed': result.records_processed,
                'file_hash': result.file_hash,
                'processing_time': result.processing_time
            }
            
            self.kafka_streamer.send_to_analytics_queue(kafka_message)
            
            logger.info(f"File processing completed: {result.records_processed} records saved")
        
        return result
    
    def start_analytics_consumer(self):
        """Start Kafka consumer for analytics processing"""
        logger.info("Starting analytics consumer...")
        self.kafka_streamer.consume_analytics_queue()
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get overall pipeline status"""
        
        return {
            'data_warehouse': {
                'status': 'active',
                'supported_formats': self.dwh_manager.supported_formats
            },
            'kafka_streaming': {
                'status': 'active',
                'servers': self.kafka_streamer.kafka_servers
            },
            'analytics': {
                'status': 'active',
                'supported_diseases': ['influenza', 'legionellosis', 'hepatitis_a']
            }
        }


# FastAPI endpoints for the pipeline
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db

pipeline_router = APIRouter()

@pipeline_router.post("/upload/")
async def upload_data_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload environmental or health data file for processing
    Supports ARPA Campania, ISPRA, and ISTAT data formats
    """
    
    orchestrator = DataPipelineOrchestrator(db)
    result = await orchestrator.process_file_upload(file)
    
    return {
        'success': result.success,
        'message': f"Processed {result.records_processed} records" if result.success else "Processing failed",
        'details': {
            'data_type': result.data_type,
            'records_processed': result.records_processed,
            'processing_time': result.processing_time,
            'errors': result.errors
        }
    }

@pipeline_router.get("/status/")
async def get_pipeline_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get data pipeline status"""
    
    orchestrator = DataPipelineOrchestrator(db)
    return orchestrator.get_pipeline_status()

@pipeline_router.post("/trigger-analytics/")
async def trigger_analytics(
    disease: str = "influenza",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Manually trigger analytics for a specific disease"""
    
    if disease not in ['influenza', 'legionellosis', 'hepatitis_a']:
        raise HTTPException(400, f"Unsupported disease: {disease}")
    
    # Trigger analytics via Kafka
    orchestrator = DataPipelineOrchestrator(db)
    message = {
        'data_type': 'manual_trigger',
        'disease': disease,
        'timestamp': datetime.now().isoformat()
    }
    
    success = orchestrator.kafka_streamer.send_to_analytics_queue(message, "analytics_trigger")
    
    return {
        'success': success,
        'message': f"Analytics triggered for {disease}" if success else "Failed to trigger analytics"
    }
