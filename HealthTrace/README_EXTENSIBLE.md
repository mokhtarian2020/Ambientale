# HealthTrace Extensible Disease Platform

## 🎯 Overview

The HealthTrace platform has been transformed from a 3-disease focused system to a comprehensive, extensible infectious disease monitoring platform that complies with Italian environmental health specifications. The platform now supports adding new infectious diseases without code changes, automatic analytics adaptation, and dynamic API generation.

## 🚀 Platform Capabilities

### Core Diseases (Initial Focus)
- **Influenza** - Respiratory disease with air quality correlations
- **Legionellosis** - Waterborne disease with temperature/humidity factors
- **Hepatitis A** - Foodborne disease with sanitation correlations

### Extended Diseases (Italian Documentation Compliance)
- **Vector-borne**: Malaria, Dengue, Chikungunya, Zika, West Nile, TBE
- **Respiratory**: COVID-19, Tuberculosis, Measles, Rubella
- **Foodborne**: Botulism, Listeriosis
- **Neurological**: Tetanus, Encephalitis, Meningitis

## 🏗️ Architecture

### Extensible Framework Components

1. **Disease Registry** (`app/models/extensible_diseases.py`)
   - Dynamic disease registration
   - Profile-based configuration
   - Category management

2. **Analytics Engine** (`analytics/advanced_models.py`)
   - Automatic model adaptation
   - Disease-specific algorithms
   - Environmental correlation analysis

3. **Dynamic APIs** (`app/api/v1/endpoints/dynamic_diseases.py`)
   - Auto-generated endpoints
   - Consistent patterns
   - Disease-agnostic operations

4. **Integration Layer** (`app/core/extensible_integration.py`)
   - Legacy compatibility
   - Migration management
   - System validation

## 📊 Disease Profile Structure

Each disease is defined by a comprehensive profile:

```python
DiseaseProfile(
    name="Disease Name",
    code="ICD-10 Code",
    category=ExtensibleDiseaseCategory.CATEGORY,
    transmission_route=ExtensibleTransmissionRoute.ROUTE,
    incubation_period_days=X,
    environmental_factors=["factor1", "factor2", ...],
    preferred_models=["GAM", "ARIMAX", ...],
    lag_period_days=X,
    seasonal_pattern="pattern",
    geographic_risk_factors=["risk1", "risk2", ...]
)
```

## 🔧 Adding New Diseases

### Method 1: Using Pre-configured Categories

```python
from app.core.extensible_integration import expansion_manager

# Add all vector-borne diseases
expansion_manager.add_vector_borne_diseases()

# Add respiratory diseases
expansion_manager.add_respiratory_diseases()

# Add foodborne diseases  
expansion_manager.add_foodborne_diseases()

# Add neurological diseases
expansion_manager.add_neurological_diseases()
```

### Method 2: Custom Disease Addition

```python
from app.models.extensible_diseases import disease_registry, DiseaseProfile

# Define custom profile
custom_profile = DiseaseProfile(
    name="Custom Disease",
    code="X00",
    category=ExtensibleDiseaseCategory.CUSTOM,
    transmission_route=ExtensibleTransmissionRoute.CUSTOM,
    environmental_factors=["temperature", "humidity"],
    preferred_models=["GAM", "RandomForest"]
)

# Register disease
disease_registry.register_disease("custom_disease", custom_profile)
```

## 📡 API Endpoints

### Core Endpoints

```
GET    /api/v1/diseases/                     # List all diseases
GET    /api/v1/diseases/categories/          # List categories  
GET    /api/v1/diseases/{name}/profile/      # Get disease profile
POST   /api/v1/diseases/{name}/analyze/      # Analyze correlations
POST   /api/v1/diseases/compare/             # Compare diseases
GET    /api/v1/diseases/{name}/environmental-factors/  # Get factors
POST   /api/v1/diseases/expand/              # Add new categories (Admin)
```

### Legacy Compatibility

```
/api/v1/influenza/     -> /api/v1/diseases/influenza/
/api/v1/legionellosis/ -> /api/v1/diseases/legionellosis/  
/api/v1/hepatitis-a/   -> /api/v1/diseases/hepatitis_a/
```

## 🧮 Analytics Models

### Available Models
- **GAM** (Generalized Additive Models)
- **GLM** (Generalized Linear Models)  
- **ARIMAX** (Time series with external regressors)
- **DLNM** (Distributed Lag Non-linear Models)
- **Random Forest** (Machine Learning)
- **XGBoost** (Gradient Boosting)
- **Spatial Models** (Geographic analysis)

### Automatic Model Selection
The system automatically selects appropriate models based on:
- Disease category
- Environmental factors
- Data characteristics
- Preferred models in disease profile

## 🌍 Italian Environmental Health Compliance

### Data Sources Integration
- **ARPA Campania** - Regional environmental monitoring
- **ISPRA** - National environmental data
- **ISTAT** - Statistical and demographic data
- **Regional Weather Stations** - Meteorological data

### Compliance Features
- ICD-10 coding standards
- Italian data format validation
- Regional ISTAT code support
- Environmental factor normalization
- Regulatory reporting capabilities

## 💾 Database Schema

### Extensible Tables

```sql
-- Main diseases registry
CREATE TABLE extensible_diseases (
    id SERIAL PRIMARY KEY,
    disease_name VARCHAR(100) UNIQUE,
    display_name VARCHAR(200),
    icd_code VARCHAR(10),
    category VARCHAR(50),
    transmission_route VARCHAR(50),
    environmental_factors JSONB,
    preferred_models JSONB,
    -- ... additional fields
);

-- Disease cases
CREATE TABLE extensible_disease_cases (
    id SERIAL PRIMARY KEY,
    disease_name VARCHAR(100) REFERENCES extensible_diseases(disease_name),
    case_date DATE,
    istat_code VARCHAR(10),
    environmental_data JSONB,
    -- ... case details
);
```

## 🚦 Quick Start

### 1. Initialize System

```python
from app.core.extensible_integration import initialize_extensible_system

# Initialize with existing diseases
result = initialize_extensible_system()
print(f"System ready with {result['total_diseases_available']} diseases")
```

### 2. Expand to Italian Diseases

```python
from app.core.extensible_integration import expand_to_italian_diseases

# Add all Italian documentation diseases
result = expand_to_italian_diseases()
print(f"Added {result['diseases_added']} new diseases")
```

### 3. Validate System

```python
from app.core.extensible_integration import validate_system_readiness

# Check system readiness
result = validate_system_readiness()
if result['overall_ready']:
    print("✅ System ready for disease extensions")
```

### 4. Run Database Migration

```python
from app.core.extensible_integration import get_migration_script

# Get migration SQL
migration_sql = get_migration_script()
# Run against database
```

## 🔍 Demo Script

Run the comprehensive demonstration:

```bash
cd /home/amir/Documents/amir/Ambientale/HealthTrace
python demo_disease_extension.py
```

This demonstrates:
- System initialization
- Disease expansion
- Analytics capabilities
- API generation
- Configuration export

## 📈 Benefits

### For Development
- **Zero Downtime**: Add diseases without system restart
- **Consistent APIs**: Automatic endpoint generation
- **Type Safety**: Strongly typed disease profiles
- **Testing**: Automated validation and testing

### For Operations
- **Scalability**: Support unlimited diseases
- **Monitoring**: Comprehensive health checks
- **Compliance**: Italian regulatory alignment
- **Maintenance**: Self-documenting system

### For Analysis
- **Flexibility**: Custom environmental factors
- **Intelligence**: Automatic model selection
- **Performance**: Optimized for each disease type
- **Accuracy**: Disease-specific lag periods and patterns

## 🎯 Italian Documentation Diseases

The platform now supports ALL infectious diseases mentioned in the Italian environmental health documentation:

| Category | Diseases | Environmental Factors |
|----------|----------|----------------------|
| **Vector-borne** | Malaria, Dengue, Chikungunya, Zika, West Nile, TBE | Temperature, Humidity, Precipitation, Vector habitat |
| **Respiratory** | COVID-19, Tuberculosis, Measles, Rubella, Influenza | Air quality, PM2.5, PM10, Temperature |
| **Waterborne** | Legionellosis | Water quality, Temperature, pH, Cooling systems |
| **Foodborne** | Hepatitis A, Botulism, Listeriosis | Temperature, Sanitation, Food safety |
| **Neurological** | Tetanus, Encephalitis, Meningitis | Various environmental and social factors |

## 🔮 Future Extensions

The platform is designed to easily accommodate:

- **Emerging Diseases**: New infectious diseases
- **Climate Change**: New environmental factors
- **AI Models**: Advanced machine learning algorithms
- **Real-time Data**: Streaming analytics
- **Global Expansion**: Multi-country support

## 🛠️ Configuration Files

### Key Configuration
- `system_config.json` - Complete system status
- `requirements.txt` - Updated dependencies
- Database migrations - SQL scripts for new tables

### Monitoring
- Health checks for all disease modules
- Performance metrics per disease
- Data quality validation
- Alert system for anomalies

---

**The HealthTrace platform is now a future-proof, extensible infectious disease monitoring system that meets Italian environmental health requirements while providing unlimited expansion capabilities.**
