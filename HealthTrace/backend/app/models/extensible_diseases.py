"""
Extensible Disease Framework for HealthTrace Platform
Supports adding new infectious diseases with their specific environmental correlations.

Current Target Diseases (Phase 1):
1. Influenza (Respiratory)
2. Legionellosis (Water-Aerosol Respiratory)  
3. Hepatitis A (Waterborne/Foodborne)

Future Diseases from Documentation:
- Vector-borne: Malaria, Dengue, Chikungunya, Zika, West Nile Virus, TBE
- Respiratory: COVID-19, Tuberculosis, Measles, Rubella
- Foodborne: Botulism, Listeriosis
- Neurological: Tetanus, Encephalitis, Meningitis
- Zoonotic: Various animal-transmitted diseases
- Syndemic combinations: HIV/AIDS + environmental factors
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type, Union
from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Date, ForeignKey, Float, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import pandas as pd
import numpy as np

from app.core.database import Base
from analytics.advanced_models import ComprehensiveAnalyzer


@dataclass
class DiseaseProfile:
    """Standard disease profile for extensibility"""
    name: str
    code: str  # ICD-10 or custom code
    category: str
    transmission_route: str
    incubation_period_days: int
    environmental_factors: List[str]
    preferred_models: List[str]
    lag_period_days: int
    seasonal_pattern: Optional[Dict[str, float]] = None
    geographic_risk_factors: Optional[List[str]] = None


class ExtensibleDiseaseCategory(enum.Enum):
    """Extended disease categories for future diseases"""
    RESPIRATORY = "respiratory"
    WATERBORNE = "waterborne"
    FOODBORNE = "foodborne"
    VECTOR_BORNE = "vector_borne"
    AIRBORNE = "airborne"
    ZOONOTIC = "zoonotic"
    NEUROLOGICAL = "neurological"
    SYNDEMIC = "syndemic"
    NOSOCOMIAL = "nosocomial"
    EMERGING = "emerging"


class ExtensibleTransmissionRoute(enum.Enum):
    """Extended transmission routes"""
    AIRBORNE_DROPLETS = "airborne_droplets"
    WATER_AEROSOL = "water_aerosol"
    CONTAMINATED_WATER = "contaminated_water"
    CONTAMINATED_FOOD = "contaminated_food"
    DIRECT_CONTACT = "direct_contact"
    VECTOR_MOSQUITO = "vector_mosquito"
    VECTOR_TICK = "vector_tick"
    VECTOR_OTHER = "vector_other"
    FECAL_ORAL = "fecal_oral"
    BLOODBORNE = "bloodborne"
    SEXUAL = "sexual"
    MATERNAL = "maternal"
    SOIL = "soil"
    ANIMAL_CONTACT = "animal_contact"


class BaseDiseaseModel(ABC, Base):
    """
    Abstract base class for all disease models
    Ensures consistent structure for extensibility
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core patient and geographic information (common to all diseases)
    patient_id = Column(String, nullable=False, index=True)
    istat_code = Column(String, nullable=False, index=True)
    
    # Case details (common to all diseases)
    onset_date = Column(Date, nullable=False, index=True)
    notification_date = Column(Date, nullable=False)
    case_status = Column(String, nullable=False)  # Suspected, Probable, Confirmed
    
    # Environmental exposure data (customizable per disease)
    environmental_exposure = Column(JSON, nullable=True)
    
    # Clinical data (disease-specific, stored as JSON for flexibility)
    clinical_data = Column(JSON, nullable=True)
    
    # Laboratory data (disease-specific)
    laboratory_data = Column(JSON, nullable=True)
    
    # Risk factors
    risk_factors = Column(JSON, nullable=True)
    
    # Outcome tracking
    outcome = Column(String, nullable=True)
    outcome_date = Column(Date, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @abstractmethod
    def get_disease_profile(self) -> DiseaseProfile:
        """Return disease-specific profile"""
        pass
    
    @abstractmethod
    def get_environmental_exposure_fields(self) -> List[str]:
        """Return list of relevant environmental factors for this disease"""
        pass
    
    @abstractmethod
    def calculate_exposure_score(self, environmental_data: Dict[str, float]) -> float:
        """Calculate disease-specific environmental exposure score"""
        pass


class DiseaseRegistry:
    """
    Registry for all disease models and their configurations
    Enables dynamic disease loading and management
    """
    
    def __init__(self):
        self._diseases: Dict[str, Type[BaseDiseaseModel]] = {}
        self._profiles: Dict[str, DiseaseProfile] = {}
        self._initialize_phase1_diseases()
    
    def _initialize_phase1_diseases(self):
        """Initialize current 3 target diseases"""
        
        # Influenza
        influenza_profile = DiseaseProfile(
            name="Influenza",
            code="J09-J11",
            category="respiratory",
            transmission_route="airborne_droplets",
            incubation_period_days=2,
            environmental_factors=["pm25", "pm10", "no2", "so2", "temperature", "humidity"],
            preferred_models=["GAM", "ARIMAX", "Random Forest"],
            lag_period_days=7,
            seasonal_pattern={"winter": 3.5, "spring": 1.2, "summer": 0.3, "autumn": 1.8}
        )
        
        # Legionellosis
        legionellosis_profile = DiseaseProfile(
            name="Legionellosis",
            code="A48.1",
            category="respiratory",
            transmission_route="water_aerosol",
            incubation_period_days=7,
            environmental_factors=["temperature", "humidity", "precipitation", "water_temperature"],
            preferred_models=["DLNM", "Spatial Analysis", "GAM"],
            lag_period_days=14
        )
        
        # Hepatitis A
        hepatitis_a_profile = DiseaseProfile(
            name="Hepatitis A",
            code="B15",
            category="waterborne",
            transmission_route="contaminated_water",
            incubation_period_days=21,
            environmental_factors=["precipitation", "flooding", "water_ph", "ecoli_count"],
            preferred_models=["DLNM", "XGBoost", "Spatial Analysis"],
            lag_period_days=21
        )
        
        self._profiles.update({
            "influenza": influenza_profile,
            "legionellosis": legionellosis_profile,
            "hepatitis_a": hepatitis_a_profile
        })
    
    def register_disease(self, disease_name: str, model_class: Type[BaseDiseaseModel], profile: DiseaseProfile):
        """Register a new disease in the system"""
        self._diseases[disease_name] = model_class
        self._profiles[disease_name] = profile
        print(f"✅ Registered disease: {disease_name}")
    
    def get_disease_model(self, disease_name: str) -> Type[BaseDiseaseModel]:
        """Get disease model class by name"""
        return self._diseases.get(disease_name)
    
    def get_disease_profile(self, disease_name: str) -> DiseaseProfile:
        """Get disease profile by name"""
        return self._profiles.get(disease_name)
    
    def list_diseases(self) -> List[str]:
        """List all registered diseases"""
        return list(self._profiles.keys())
    
    def get_diseases_by_category(self, category: str) -> List[str]:
        """Get all diseases in a specific category"""
        return [name for name, profile in self._profiles.items() 
                if profile.category == category]
    
    def get_diseases_by_environmental_factor(self, factor: str) -> List[str]:
        """Get diseases affected by a specific environmental factor"""
        return [name for name, profile in self._profiles.items() 
                if factor in profile.environmental_factors]


class FutureDiseaseTemplate:
    """
    Template for quickly adding new diseases
    Provides pre-configured profiles for diseases mentioned in documentation
    """
    
    @staticmethod
    def get_vector_borne_diseases() -> Dict[str, DiseaseProfile]:
        """Vector-borne diseases from documentation"""
        return {
            "malaria": DiseaseProfile(
                name="Malaria",
                code="B50-B54",
                category="vector_borne",
                transmission_route="vector_mosquito",
                incubation_period_days=14,
                environmental_factors=["temperature", "humidity", "precipitation", "standing_water"],
                preferred_models=["MaxEnt", "Random Forest", "GAM"],
                lag_period_days=14,
                seasonal_pattern={"wet_season": 4.0, "dry_season": 0.5}
            ),
            
            "dengue": DiseaseProfile(
                name="Dengue",
                code="A90-A91",
                category="vector_borne",
                transmission_route="vector_mosquito",
                incubation_period_days=7,
                environmental_factors=["temperature", "humidity", "precipitation", "urban_water_storage"],
                preferred_models=["LSTM", "XGBoost", "Spatial Analysis"],
                lag_period_days=10
            ),
            
            "chikungunya": DiseaseProfile(
                name="Chikungunya",
                code="A92.0",
                category="vector_borne",
                transmission_route="vector_mosquito",
                incubation_period_days=5,
                environmental_factors=["temperature", "humidity", "precipitation"],
                preferred_models=["ARIMAX", "Random Forest"],
                lag_period_days=7
            ),
            
            "zika": DiseaseProfile(
                name="Zika Virus",
                code="A92.5",
                category="vector_borne",
                transmission_route="vector_mosquito",
                incubation_period_days=7,
                environmental_factors=["temperature", "humidity", "urban_development"],
                preferred_models=["Spatial Analysis", "LSTM"],
                lag_period_days=10
            ),
            
            "west_nile": DiseaseProfile(
                name="West Nile Virus",
                code="A92.3",
                category="vector_borne",
                transmission_route="vector_mosquito",
                incubation_period_days=14,
                environmental_factors=["temperature", "precipitation", "bird_migration"],
                preferred_models=["Spatial Analysis", "ARIMAX"],
                lag_period_days=21
            ),
            
            "tbe": DiseaseProfile(
                name="Tick-Borne Encephalitis",
                code="A84",
                category="vector_borne",
                transmission_route="vector_tick",
                incubation_period_days=14,
                environmental_factors=["temperature", "humidity", "forest_coverage"],
                preferred_models=["GAM", "Spatial Analysis"],
                lag_period_days=14
            )
        }
    
    @staticmethod
    def get_respiratory_diseases() -> Dict[str, DiseaseProfile]:
        """Additional respiratory diseases"""
        return {
            "covid19": DiseaseProfile(
                name="COVID-19",
                code="U07.1",
                category="respiratory",
                transmission_route="airborne_droplets",
                incubation_period_days=5,
                environmental_factors=["pm25", "pm10", "temperature", "humidity", "uv_index"],
                preferred_models=["LSTM", "XGBoost", "Spatial Analysis"],
                lag_period_days=7,
                seasonal_pattern={"winter": 2.5, "spring": 1.5, "summer": 0.8, "autumn": 1.8}
            ),
            
            "tuberculosis": DiseaseProfile(
                name="Tuberculosis",
                code="A15-A19",
                category="respiratory",
                transmission_route="airborne_droplets",
                incubation_period_days=90,
                environmental_factors=["pm25", "pm10", "no2", "humidity", "overcrowding"],
                preferred_models=["DLNM", "Spatial Analysis", "Random Forest"],
                lag_period_days=30
            ),
            
            "measles": DiseaseProfile(
                name="Measles",
                code="B05",
                category="airborne",
                transmission_route="airborne_droplets",
                incubation_period_days=12,
                environmental_factors=["pm10", "pm25", "temperature", "humidity"],
                preferred_models=["Spatial Analysis", "ARIMAX"],
                lag_period_days=14
            ),
            
            "rubella": DiseaseProfile(
                name="Rubella",
                code="B06",
                category="airborne",
                transmission_route="airborne_droplets",
                incubation_period_days=18,
                environmental_factors=["temperature", "humidity", "pm25"],
                preferred_models=["GAM", "Spatial Analysis"],
                lag_period_days=21
            )
        }
    
    @staticmethod
    def get_foodborne_diseases() -> Dict[str, DiseaseProfile]:
        """Foodborne diseases"""
        return {
            "botulism": DiseaseProfile(
                name="Botulism",
                code="A05.1",
                category="foodborne",
                transmission_route="contaminated_food",
                incubation_period_days=1,
                environmental_factors=["temperature", "humidity", "food_storage"],
                preferred_models=["Case-Crossover", "GAM"],
                lag_period_days=3
            ),
            
            "listeriosis": DiseaseProfile(
                name="Listeriosis",
                code="A32",
                category="foodborne",
                transmission_route="contaminated_food",
                incubation_period_days=21,
                environmental_factors=["temperature", "humidity", "refrigeration"],
                preferred_models=["DLNM", "Spatial Analysis"],
                lag_period_days=21
            )
        }
    
    @staticmethod
    def get_neurological_diseases() -> Dict[str, DiseaseProfile]:
        """Neurological diseases"""
        return {
            "tetanus": DiseaseProfile(
                name="Tetanus",
                code="A33-A35",
                category="neurological",
                transmission_route="soil",
                incubation_period_days=10,
                environmental_factors=["soil_contamination", "temperature", "humidity"],
                preferred_models=["GAM", "Spatial Analysis"],
                lag_period_days=14
            ),
            
            "encephalitis": DiseaseProfile(
                name="Encephalitis",
                code="G04",
                category="neurological",
                transmission_route="airborne_droplets",
                incubation_period_days=14,
                environmental_factors=["pm25", "temperature", "humidity"],
                preferred_models=["Spatial Analysis", "DLNM"],
                lag_period_days=14
            ),
            
            "meningitis": DiseaseProfile(
                name="Meningitis",
                code="G00-G03",
                category="neurological",
                transmission_route="airborne_droplets",
                incubation_period_days=4,
                environmental_factors=["pm25", "temperature", "overcrowding"],
                preferred_models=["Spatial Analysis", "ARIMAX"],
                lag_period_days=7
            )
        }


class ExtensibleAnalyticsEngine:
    """
    Analytics engine that adapts to different diseases automatically
    """
    
    def __init__(self, disease_registry: DiseaseRegistry):
        self.registry = disease_registry
        self.analyzers: Dict[str, ComprehensiveAnalyzer] = {}
    
    def get_analyzer(self, disease_name: str) -> ComprehensiveAnalyzer:
        """Get or create analyzer for specific disease"""
        if disease_name not in self.analyzers:
            self.analyzers[disease_name] = ComprehensiveAnalyzer(disease_name)
        return self.analyzers[disease_name]
    
    def run_analysis_for_disease(self, disease_name: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Run analysis tailored to specific disease"""
        
        profile = self.registry.get_disease_profile(disease_name)
        if not profile:
            raise ValueError(f"Disease {disease_name} not registered")
        
        # Filter data based on disease profile
        relevant_factors = profile.environmental_factors
        available_factors = [f for f in relevant_factors if f in data.columns]
        
        if not available_factors:
            raise ValueError(f"No environmental factors available for {disease_name}")
        
        # Use disease-specific lag period
        if 'date' in data.columns:
            data = self._apply_lag(data, profile.lag_period_days)
        
        # Get appropriate analyzer
        analyzer = self.get_analyzer(disease_name)
        
        # Run analysis with preferred models
        results = analyzer.run_all_analyses(data)
        
        # Filter results based on preferred models
        preferred_results = {}
        for model_name in profile.preferred_models:
            if model_name in results:
                preferred_results[model_name] = results[model_name]
        
        return {
            'disease': disease_name,
            'profile': profile,
            'results': preferred_results,
            'available_factors': available_factors,
            'total_models_run': len(results),
            'preferred_models_run': len(preferred_results)
        }
    
    def _apply_lag(self, data: pd.DataFrame, lag_days: int) -> pd.DataFrame:
        """Apply disease-specific lag to environmental data"""
        lagged_data = data.copy()
        
        # Create lagged environmental variables
        env_columns = ['pm25', 'pm10', 'ozone', 'no2', 'so2', 'temperature', 'humidity', 'precipitation']
        
        for col in env_columns:
            if col in data.columns:
                lagged_data[f'{col}_lag_{lag_days}'] = data[col].shift(lag_days)
        
        return lagged_data.dropna()
    
    def compare_diseases(self, diseases: List[str], data: pd.DataFrame) -> pd.DataFrame:
        """Compare multiple diseases side by side"""
        
        comparison_results = []
        
        for disease in diseases:
            try:
                result = self.run_analysis_for_disease(disease, data)
                
                # Extract best model performance
                best_model = max(result['results'].items(), 
                               key=lambda x: x[1].r_squared) if result['results'] else None
                
                if best_model:
                    comparison_results.append({
                        'Disease': disease,
                        'Category': result['profile'].category,
                        'Best_Model': best_model[0],
                        'R_Squared': best_model[1].r_squared,
                        'MAE': best_model[1].mae,
                        'Key_Factors': ', '.join(result['available_factors'][:3])
                    })
                    
            except Exception as e:
                print(f"Error analyzing {disease}: {str(e)}")
        
        return pd.DataFrame(comparison_results)


class DiseaseExpansionManager:
    """
    Manager for adding new diseases to the platform
    """
    
    def __init__(self, registry: DiseaseRegistry):
        self.registry = registry
        self.templates = FutureDiseaseTemplate()
    
    def add_vector_borne_diseases(self):
        """Add all vector-borne diseases from templates"""
        diseases = self.templates.get_vector_borne_diseases()
        
        for name, profile in diseases.items():
            # Create dynamic model class
            model_class = self._create_disease_model_class(name, profile)
            self.registry.register_disease(name, model_class, profile)
    
    def add_respiratory_diseases(self):
        """Add additional respiratory diseases"""
        diseases = self.templates.get_respiratory_diseases()
        
        for name, profile in diseases.items():
            model_class = self._create_disease_model_class(name, profile)
            self.registry.register_disease(name, model_class, profile)
    
    def add_foodborne_diseases(self):
        """Add foodborne diseases"""
        diseases = self.templates.get_foodborne_diseases()
        
        for name, profile in diseases.items():
            model_class = self._create_disease_model_class(name, profile)
            self.registry.register_disease(name, model_class, profile)
    
    def add_neurological_diseases(self):
        """Add neurological diseases"""
        diseases = self.templates.get_neurological_diseases()
        
        for name, profile in diseases.items():
            model_class = self._create_disease_model_class(name, profile)
            self.registry.register_disease(name, model_class, profile)
    
    def add_custom_disease(self, name: str, profile: DiseaseProfile):
        """Add a completely custom disease"""
        model_class = self._create_disease_model_class(name, profile)
        self.registry.register_disease(name, model_class, profile)
    
    def _create_disease_model_class(self, name: str, profile: DiseaseProfile) -> Type[BaseDiseaseModel]:
        """Dynamically create a disease model class"""
        
        class_name = f"{name.replace('_', '').title()}Case"
        table_name = f"{name}_cases"
        
        # Create class attributes
        attrs = {
            '__tablename__': table_name,
            '__module__': __name__,
            
            # Disease-specific implementation
            'get_disease_profile': lambda self: profile,
            'get_environmental_exposure_fields': lambda self: profile.environmental_factors,
            'calculate_exposure_score': lambda self, env_data: self._default_exposure_score(env_data),
            '_default_exposure_score': lambda self, env_data: sum(env_data.values()) / len(env_data)
        }
        
        # Create the class dynamically
        model_class = type(class_name, (BaseDiseaseModel,), attrs)
        
        return model_class
    
    def bulk_add_future_diseases(self):
        """Add all pre-configured future diseases"""
        print("🚀 Adding future diseases to HealthTrace platform...")
        
        self.add_vector_borne_diseases()
        self.add_respiratory_diseases()
        self.add_foodborne_diseases()
        self.add_neurological_diseases()
        
        print(f"✅ Added {len(self.registry.list_diseases()) - 3} new diseases")
        print(f"📊 Total diseases now supported: {len(self.registry.list_diseases())}")


# Global registry instance
disease_registry = DiseaseRegistry()
analytics_engine = ExtensibleAnalyticsEngine(disease_registry)
expansion_manager = DiseaseExpansionManager(disease_registry)


def demonstrate_extensibility():
    """Demonstrate how easily new diseases can be added"""
    
    print("=== HealthTrace Disease Extensibility Demo ===\n")
    
    # Show current diseases
    print("📋 Current diseases (Phase 1):")
    for disease in disease_registry.list_diseases():
        profile = disease_registry.get_disease_profile(disease)
        print(f"  • {profile.name} ({profile.category})")
    
    print(f"\n🔧 Adding future diseases...")
    
    # Add all future diseases
    expansion_manager.bulk_add_future_diseases()
    
    # Show expanded list
    print("\n📋 All diseases after expansion:")
    for disease in disease_registry.list_diseases():
        profile = disease_registry.get_disease_profile(disease)
        print(f"  • {profile.name} ({profile.category}) - {len(profile.environmental_factors)} factors")
    
    # Show diseases by category
    print("\n📊 Diseases by category:")
    categories = set(profile.category for profile in disease_registry._profiles.values())
    for category in categories:
        diseases = disease_registry.get_diseases_by_category(category)
        print(f"  • {category.title()}: {len(diseases)} diseases")
    
    # Show diseases affected by specific environmental factors
    print("\n🌍 Diseases affected by PM2.5:")
    pm25_diseases = disease_registry.get_diseases_by_environmental_factor("pm25")
    for disease in pm25_diseases:
        profile = disease_registry.get_disease_profile(disease)
        print(f"  • {profile.name}")
    
    print("\n✅ Platform now supports comprehensive infectious disease monitoring!")


if __name__ == "__main__":
    demonstrate_extensibility()
