# Detailed Kafka Data Ingestion Process - HealthTrace Project

## Overview

The HealthTrace project uses **Apache Kafka** as the central messaging system for real-time data streaming and processing. The ingestion process follows a structured pipeline that handles environmental, health, and climate data from multiple sources.

---

## 1. Architecture Overview

```
Data Sources → API/File Upload → Data Warehouse → Kafka Topics → Analytics Consumers → API Endpoints
```

### Components:
- **Kafka Broker**: Confluent Kafka (Docker container)
- **Zookeeper**: Coordination service for Kafka
- **Producers**: Applications that send data to Kafka
- **Consumers**: Applications that process data from Kafka
- **Topics**: Logical channels for different data types

---

## 2. Kafka Infrastructure Setup

### Docker Configuration
```yaml
# From docker-compose.yml
kafka:
  image: confluentinc/cp-kafka:latest
  container_name: healthtrace_kafka
  depends_on:
    - zookeeper
  environment:
    KAFKA_BROKER_ID: 1
    KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
    KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
    KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
    KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    KAFKA_AUTO_CREATE_TOPICS_ENABLE: true
  ports:
    - "29092:29092"
```

### Topic Configuration
```python
# From app/core/config.py
KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
KAFKA_TOPIC_ENVIRONMENTAL: str = "environmental-data"
KAFKA_TOPIC_HEALTH: str = "health-data"
```

---

## 3. Data Ingestion Flow

### Step 1: Data Sources
The system ingests data from multiple sources:
- **ARPA Campania**: Air quality measurements (PM10, PM2.5, NO2, O3, etc.)
- **ISPRA**: Environmental indicators
- **ISTAT**: Weather and demographic data
- **Health Authorities**: Disease case reports (Influenza, Legionellosis, Hepatitis A)

### Step 2: Data Collection Methods

#### A. File Upload (Batch Processing)
```python
# From data_pipeline.py
class DataPipelineOrchestrator:
    async def process_file_upload(self, file: UploadFile) -> FileProcessingResult:
        # Step 1: Process file and save to Data Warehouse
        result = self.dwh_manager.process_file(file)
        
        if result.success:
            # Step 2: Send notification to Kafka
            kafka_message = {
                'data_type': result.data_type,
                'records_processed': result.records_processed,
                'file_hash': result.file_hash,
                'processing_time': result.processing_time
            }
            
            # Send to Kafka for analytics processing
            self.kafka_streamer.send_to_analytics_queue(kafka_message)
```

#### B. External API Ingestion
```python
# From data_ingestion.py
class ExternalDataIngestion:
    async def fetch_ispra_data(self, pollutant: str, region: str = None):
        """Fetch data from ISPRA environmental indicators"""
        # API call implementation
        
    async def fetch_arpa_data(self, station_id: str, pollutant: str):
        """Fetch data from ARPA Campania"""
        # API call implementation
```

---

## 4. Kafka Producer Implementation

### Environmental Data Producer
```python
# From kafka_producer.py
class EnvironmentalDataProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',           # Wait for all replicas to acknowledge
            retries=3,            # Retry failed sends
            retry_backoff_ms=1000 # Wait time between retries
        )

    def send_environmental_data(self, data: Dict[str, Any], key: Optional[str] = None) -> bool:
        """Send environmental data to Kafka topic"""
        try:
            # Add metadata wrapper
            message = {
                "timestamp": datetime.utcnow().isoformat(),
                "data_type": "environmental",
                "source": "healthtrace_api",
                "payload": data
            }
            
            # Send to Kafka with partitioning key (istat_code)
            future = self.producer.send(
                settings.KAFKA_TOPIC_ENVIRONMENTAL,
                value=message,
                key=key or data.get('istat_code')
            )
            
            # Wait for confirmation
            result = future.get(timeout=10)
            logger.info(f"Environmental data sent to Kafka: {result}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send environmental data: {e}")
            return False

    def send_health_data(self, data: Dict[str, Any], key: Optional[str] = None) -> bool:
        """Send health/disease data to Kafka topic"""
        # Similar implementation for health data
```

### Message Structure
```json
{
  "timestamp": "2026-02-24T10:30:00Z",
  "data_type": "environmental",
  "source": "healthtrace_api",
  "payload": {
    "istat_code": "063049",
    "station_code": "NA01",
    "station_name": "Napoli Centro",
    "latitude": 40.8518,
    "longitude": 14.2681,
    "measurement_date": "2026-02-24",
    "pm10": 35.5,
    "pm25": 22.1,
    "no2": 45.2,
    "ozone": 88.7,
    "pollutant_values": {...}
  }
}
```

---

## 5. Kafka Consumer Implementation

### Analytics Consumer
```python
# From data_pipeline.py
class KafkaDataStreamer:
    def consume_analytics_queue(self, topic: str = "environmental_data"):
        """Consume messages from Kafka for analytics processing"""
        
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.kafka_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='analytics_processor',    # Consumer group for parallel processing
            auto_offset_reset='latest',        # Start from latest messages
            enable_auto_commit=True,           # Auto-commit offsets
            auto_commit_interval_ms=1000       # Commit every second
        )
        
        for message in consumer:
            try:
                data = message.value
                self.process_analytics_message(data)
            except Exception as e:
                logger.error(f"Error processing Kafka message: {str(e)}")

    def process_analytics_message(self, message: Dict[str, Any]):
        """Route message to appropriate analytics processor"""
        
        data_type = message.get('data_type')
        data = message.get('data')
        
        if data_type == 'environmental':
            self.trigger_environmental_analytics(data)
        elif data_type == 'climate':
            self.trigger_climate_analytics(data)
        elif data_type == 'health':
            self.trigger_health_analytics(data)
```

---

## 6. Data Processing and Analytics Pipeline

### Environmental Analytics Trigger
```python
def trigger_environmental_analytics(self, data: Dict[str, Any]):
    """Trigger environmental analytics processing"""
    
    try:
        # Create analyzer for each disease
        diseases = ['influenza', 'legionellosis', 'hepatitis_a']
        
        for disease in diseases:
            analyzer = ComprehensiveAnalyzer(disease)
            
            # Fetch related data from database
            sample_df = pd.DataFrame([data])
            
            if not sample_df.empty:
                # Run statistical and ML analyses
                results = analyzer.run_all_analyses(sample_df)
                logger.info(f"Analytics completed for {disease}: {len(results)} models")
                
                # Store results and trigger alerts if needed
                
    except Exception as e:
        logger.error(f"Error in environmental analytics: {str(e)}")
```

---

## 7. Data Validation and Quality Control

### Input Validation
```python
def validate_environmental_message(self, message: Dict[str, Any]) -> bool:
    """Validate incoming environmental data message"""
    
    required_fields = ['istat_code', 'measurement_date', 'station_code']
    
    # Check required fields
    for field in required_fields:
        if field not in message.get('payload', {}):
            logger.error(f"Missing required field: {field}")
            return False
    
    # Validate data types and ranges
    payload = message['payload']
    
    # Validate pollutant values
    pollutant_ranges = {
        'pm10': (0, 500),
        'pm25': (0, 300),
        'no2': (0, 400),
        'ozone': (0, 600)
    }
    
    for pollutant, (min_val, max_val) in pollutant_ranges.items():
        if pollutant in payload:
            value = payload[pollutant]
            if not (min_val <= value <= max_val):
                logger.warning(f"Pollutant {pollutant} value out of range: {value}")
    
    return True
```

---

## 8. Error Handling and Monitoring

### Dead Letter Queue
```python
def handle_processing_error(self, message: Dict[str, Any], error: Exception):
    """Handle messages that fail processing"""
    
    # Send to dead letter topic for manual inspection
    error_message = {
        'original_message': message,
        'error': str(error),
        'timestamp': datetime.utcnow().isoformat(),
        'processing_attempt': message.get('retry_count', 0) + 1
    }
    
    self.producer.send('environmental-data-errors', value=error_message)
```

### Monitoring Metrics
- **Message throughput**: Messages per second
- **Processing latency**: Time from ingestion to processing
- **Error rate**: Failed message percentage
- **Consumer lag**: Offset lag for each consumer group

---

## 9. Scaling and Performance Considerations

### Partitioning Strategy
- **Environmental data**: Partitioned by `istat_code` (geographic distribution)
- **Health data**: Partitioned by `patient_id` or `region_code`
- **Climate data**: Partitioned by `station_id`

### Consumer Scaling
```python
# Multiple consumer instances in the same group
# Each instance processes different partitions
consumer_config = {
    'group_id': 'analytics_processor',
    'max_poll_records': 500,          # Batch size
    'session_timeout_ms': 30000,      # Session timeout
    'heartbeat_interval_ms': 3000,    # Heartbeat interval
    'max_poll_interval_ms': 300000    # Max poll interval
}
```

---

## 10. Integration with HealthTrace Components

### Dashboard Integration
```python
# Real-time data for dashboards
def stream_to_dashboard(self, processed_data: Dict[str, Any]):
    """Send processed data to dashboard via WebSocket"""
    
    dashboard_message = {
        'type': 'environmental_update',
        'data': processed_data,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Send to WebSocket connections or API endpoints
    websocket_manager.broadcast(dashboard_message)
```

### Alert System Integration
```python
def trigger_alerts(self, analysis_results: Dict[str, Any]):
    """Trigger alerts based on analysis results"""
    
    # Check thresholds
    if analysis_results.get('risk_level') == 'HIGH':
        alert_message = {
            'alert_type': 'environmental_risk',
            'severity': 'HIGH',
            'location': analysis_results.get('location'),
            'pollutants': analysis_results.get('exceeded_pollutants'),
            'recommendations': analysis_results.get('recommendations')
        }
        
        # Send to alert topic
        self.producer.send('alerts', value=alert_message)
```

---

## Summary

The Kafka ingestion process in HealthTrace provides:

1. **Real-time streaming** of environmental and health data
2. **Scalable processing** with consumer groups and partitioning
3. **Fault tolerance** with retries and dead letter queues
4. **Data validation** and quality control
5. **Integration** with analytics, dashboards, and alerting systems

This architecture ensures reliable, scalable, and real-time processing of environmental and health data for correlation analysis and public health monitoring.
