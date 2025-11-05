"""
Kafka Producer for Environmental Data Streaming

This module handles real-time streaming of environmental data to Kafka topics
based on the architecture diagram in Section 3.2.
"""

import json
import logging
from typing import Dict, Any, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
from datetime import datetime

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnvironmentalDataProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',
            retries=3,
            retry_backoff_ms=1000
        )
    
    def send_environmental_data(self, data: Dict[str, Any], key: Optional[str] = None) -> bool:
        """
        Send environmental data to Kafka topic
        
        Args:
            data: Environmental data dictionary
            key: Optional partition key (e.g., istat_code)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add metadata
            message = {
                "timestamp": datetime.utcnow().isoformat(),
                "data_type": "environmental",
                "source": "healthtrace_api",
                "payload": data
            }
            
            # Send to Kafka
            future = self.producer.send(
                settings.KAFKA_TOPIC_ENVIRONMENTAL,
                value=message,
                key=key or data.get('istat_code')
            )
            
            # Wait for result
            result = future.get(timeout=10)
            logger.info(f"Environmental data sent to Kafka: {result}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send environmental data: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    def send_health_data(self, data: Dict[str, Any], key: Optional[str] = None) -> bool:
        """
        Send health/disease data to Kafka topic
        
        Args:
            data: Health data dictionary
            key: Optional partition key (e.g., patient_id)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add metadata
            message = {
                "timestamp": datetime.utcnow().isoformat(),
                "data_type": "health",
                "source": "healthtrace_api",
                "payload": data
            }
            
            # Send to Kafka
            future = self.producer.send(
                settings.KAFKA_TOPIC_HEALTH,
                value=message,
                key=key or str(data.get('patient_id'))
            )
            
            # Wait for result
            result = future.get(timeout=10)
            logger.info(f"Health data sent to Kafka: {result}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send health data: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    def close(self):
        """Close the Kafka producer"""
        if self.producer:
            self.producer.close()


# Global producer instance
producer = EnvironmentalDataProducer()
