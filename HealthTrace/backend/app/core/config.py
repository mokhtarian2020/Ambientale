from typing import List, Union
from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://healthtrace:password@localhost/healthtrace"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_ENVIRONMENTAL: str = "environmental-data"
    KAFKA_TOPIC_HEALTH: str = "health-data"
    
    # External APIs
    ISTAT_API_BASE_URL: str = "https://www.istat.it/api"
    ISPRA_API_BASE_URL: str = "https://indicatoriambientali.isprambiente.it/api"
    ARPA_CAMPANIA_API_BASE_URL: str = "https://dati.arpacampania.it/api"
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Analytics
    MODELS_DIR: str = "./models"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
