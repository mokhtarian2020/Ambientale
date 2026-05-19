# HealthTrace - Technical Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Database Design](#database-design)
3. [API Documentation](#api-documentation)
4. [Frontend Components](#frontend-components)
5. [Data Pipeline](#data-pipeline)
6. [Analytics and ML Models](#analytics-and-ml-models)
7. [Deployment Guide](#deployment-guide)
8. [User Roles and Permissions](#user-roles-and-permissions)
9. [Legal Compliance](#legal-compliance)
10. [Correlation Analysis](#correlation-analysis)

## System Architecture

### Overview
HealthTrace follows a microservices architecture with the following components:

```
┌─────────────────────────────────────────────────────────────────┐
│                    HealthTrace Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Frontend   │    │   Backend    │    │  Analytics   │      │
│  │   (React)    │◄──►│  (FastAPI)   │◄──►│  (Python)    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │Data Pipeline │    │  Database    │    │    Kafka     │      │
│  │  (Python)    │◄──►│(PostgreSQL/  │◄──►│ (Streaming)  │      │
│  │              │    │ TimescaleDB) │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Backend
- **FastAPI**: Modern Python web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **PostgreSQL**: Primary database with TimescaleDB extension
- **Kafka**: Event streaming platform for real-time data processing
- **Redis**: Caching and session management

#### Frontend
- **React**: JavaScript library for building user interfaces
- **Material-UI**: React component library
- **React Router**: Declarative routing for React
- **Axios**: Promise-based HTTP client
- **Recharts**: Chart library for React
- **Leaflet**: Interactive maps

#### Data & Analytics
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: Machine learning library
- **NumPy**: Numerical computing
- **GeoPandas**: Geographic data analysis
- **Plotly**: Interactive plotting

#### Infrastructure
- **Docker**: Containerization platform
- **Nginx**: Web server and reverse proxy
- **Docker Compose**: Multi-container Docker applications

## Database Design

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    telephone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TYPE user_role AS ENUM ('mmg', 'pls', 'uosd', 'uoc_epidemiology', 'admin');
```

#### Patients Table
```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    tax_code VARCHAR(16) UNIQUE,
    stp_code VARCHAR(50),
    eni_code VARCHAR(50),
    surname VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    gender gender NOT NULL,
    birth_date DATE NOT NULL,
    birth_country VARCHAR(255),
    birth_province VARCHAR(255),
    birth_municipality VARCHAR(255) NOT NULL,
    profession VARCHAR(255),
    residence_address TEXT,
    residence_municipality VARCHAR(255),
    residence_province VARCHAR(255),
    residence_region VARCHAR(255),
    telephone VARCHAR(50),
    status patient_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TYPE gender AS ENUM ('male', 'female', 'other');
CREATE TYPE patient_status AS ENUM ('active', 'recovered', 'deceased');
```

#### Environmental Data Table (Time-Series)
```sql
CREATE TABLE environmental_data (
    id SERIAL PRIMARY KEY,
    istat_code VARCHAR(10) NOT NULL,
    municipality VARCHAR(255) NOT NULL,
    province VARCHAR(255) NOT NULL,
    region VARCHAR(255) NOT NULL,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    altitude DECIMAL(8,2),
    measurement_date DATE NOT NULL,
    measurement_year INTEGER NOT NULL,
    measurement_month INTEGER,
    
    -- Air Quality Data
    pm10 DECIMAL(8,2),
    pm25 DECIMAL(8,2),
    ozone DECIMAL(8,2),
    no2 DECIMAL(8,2),
    so2 DECIMAL(8,2),
    co DECIMAL(8,2),
    benzene DECIMAL(8,2),
    
    -- Weather Data
    temperature_avg DECIMAL(5,2),
    temperature_max DECIMAL(5,2),
    temperature_min DECIMAL(5,2),
    humidity DECIMAL(5,2),
    precipitation DECIMAL(8,2),
    wind_speed DECIMAL(6,2),
    atmospheric_pressure DECIMAL(7,2),
    solar_radiation DECIMAL(8,2),
    
    -- Anthropic Data
    has_mines BOOLEAN DEFAULT FALSE,
    has_industries BOOLEAN DEFAULT FALSE,
    area_type VARCHAR(50),
    
    data_source VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create TimescaleDB hypertable for time-series optimization
SELECT create_hypertable('environmental_data', 'measurement_date');

-- Create indexes for performance
CREATE INDEX idx_environmental_data_istat_date ON environmental_data (istat_code, measurement_date);
CREATE INDEX idx_environmental_data_region ON environmental_data (region);
CREATE INDEX idx_environmental_data_year_month ON environmental_data (measurement_year, measurement_month);
```

### Relationships and Constraints

#### Disease Reports
```sql
CREATE TABLE disease_reports (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    reporting_doctor_id INTEGER REFERENCES users(id),
    disease_name VARCHAR(255) NOT NULL,
    uosd_diagnosis VARCHAR(255),
    symptom_onset_date DATE,
    symptom_onset_municipality VARCHAR(255),
    hospitalization BOOLEAN DEFAULT FALSE,
    vaccination_status VARCHAR(50),
    vaccination_doses INTEGER,
    last_dose_date DATE,
    vaccine_type VARCHAR(255),
    report_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## API Documentation

### Authentication Endpoints

#### POST /api/v1/auth/login
Login with username and password.

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "access_token": "string",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "username": "string",
        "full_name": "string",
        "role": "mmg|pls|uosd|uoc_epidemiology|admin",
        "email": "string"
    }
}
```

### Environmental Data Endpoints

#### GET /api/v1/environmental/istat/{istat_code}/{year}/{interval}/{function}/{pollutant}
Get pollutant data as specified in requirements.

**Parameters:**
- `istat_code`: Municipality/Province ISTAT code
- `year`: Year (e.g., 2023)
- `interval`: 0 for full year, 1-12 for specific month
- `function`: "average" or "maximum"
- `pollutant`: "pm10", "pm25", "no2", "ozone", etc.

**Example:**
```
GET /api/v1/environmental/istat/063049/2023/0/average/pm25
```

**Response:**
```json
{
    "istat_code": "063049",
    "year": 2023,
    "interval": 0,
    "function": "average",
    "pollutant": "pm25",
    "value": 22.5,
    "unit": "μg/m³",
    "records_count": 365
}
```

#### GET /api/v1/environmental/climate/{istat_code}/{year}/{interval}/{measurement}/{function}
Get climate data as specified in requirements.

**Parameters:**
- `measurement`: "precipitation", "temperature", "humidity", "wind"
- `function`: "sum", "average", "days_with_precipitation"

### Patient Management Endpoints

#### POST /api/v1/patients/
Create a new patient (CU05: Infectious Disease Reporting).

#### GET /api/v1/patients/search
Search patients by name, surname, or tax code (CU06: Patient Research).

#### GET /api/v1/patients/{patient_id}
Get patient details (CU07: View Patient).

#### PUT /api/v1/patients/{patient_id}
Update patient information (CU08: Patient Change).

### Dashboard Endpoints

#### GET /api/v1/dashboard/summary
Summary and monitoring dashboard data (CU18).

#### GET /api/v1/dashboard/geo-view
Geo-referenced data for mapping (CU19).

#### GET /api/v1/dashboard/environmental-correlation
Environmental correlation data (CU20).

## Frontend Components

### User Management Components
Based on the functional specifications:

#### CU01-CU03: User Profile Creation
- **Component**: `UserManagement.js`
- **Features**: Create MMG, PLS, U.O.S.D., and U.O.C. Epidemiology profiles
- **Permissions**: Admin only

#### CU04: System Access
- **Component**: `Login.js`
- **Features**: Authentication with role-based redirects

### Disease Reporting Components

#### CU05: Infectious Disease Reporting
- **Component**: `DiseaseReporting.js`
- **Form Fields**:
  - Disease Information: Disease name, UOSD diagnosis
  - Patient Personal Data: Tax code, name, gender, birth info
  - Clinical Data: Symptom onset, hospitalization, vaccination status
  - Reporting Data: Doctor info, report date

#### CU06-CU09: Patient Management
- **Component**: `PatientManagement.js`
- **Features**:
  - Patient search by name, surname, tax code
  - Patient view with complete record
  - Patient status updates (Active/Recovered/Deceased)
  - Disease-specific searches

### Investigation Components

#### CU10: Epidemiological Investigation
- **Component**: `EpidemiologicalInvestigation.js`
- **Features**:
  - Case type classification (Probable/Confirmed)
  - Symptomatology recording
  - Contagion source analysis
  - Contact tracing

#### CU11-CU17: Disease-Specific Forms
Specialized investigation forms for:
- **CU11**: Influenza
- **CU12**: Botulism
- **CU13**: Tetanus
- **CU14**: Encephalitis, Meningitis, Meningococcal Syndrome
- **CU15**: Legionnaires' disease
- **CU16**: Listeriosis
- **CU17**: Measles and Rubella

### Dashboard Components

#### CU18: Summary Dashboard
- **Component**: `Dashboard.js`
- **Features**:
  - Quantitative graphs (reports and investigations over time)
  - Pie charts (disease distribution, U.O.S.D. distribution)
  - Interactive filters (time period, pathology)

#### CU19: Geo-View Dashboard
- **Component**: `GeoVisualization.js`
- **Features**:
  - Interactive map with disease distribution
  - Heatmap for infection density
  - Geographic filters and zoom capabilities

#### CU20: Environmental Correlation
- **Component**: `EnvironmentalCorrelation.js`
- **Features**:
  - Data integration (PM2.5, PM10, Ozone, Humidity, Temperature)
  - Time-series correlation graphs
  - Epidemiological hypothesis exploration

## Data Pipeline

### Real-time Data Ingestion
The system implements the architecture from Section 3.2:

```
File → Data Warehouse → Kafka Broker → Algorithm → API
```

#### Data Sources Integration
1. **ISPRA**: Environmental indicators
2. **ARPA Campania**: Regional air quality data
3. **ISTAT**: Weather and demographic data

#### Kafka Topics
- `environmental-data`: Real-time environmental measurements
- `health-data`: Disease reports and investigations

#### Batch Processing
- Excel/CSV file uploads
- Data validation and transformation
- Bulk database insertion

## Analytics and ML Models

### Multiple Linear Regression (Section 3.1)
Implementation of the example model:

```
Y = β₀ + β₁×PM2.5 + β₂×O₃ + β₃×Rainy_Days + ε
```

Where:
- Y: Number of chronic bronchitis cases
- β₀: Intercept (50 in the example)
- β₁: PM2.5 coefficient (2.5 in the example)
- β₂: Ozone coefficient (1.8 in the example)
- β₃: Rainy days coefficient (-0.5 in the example)

### Time Series Models
- **ARIMA**: Autoregressive Integrated Moving Average
- **DLNM**: Distributed Lag Non-linear Models

### Machine Learning Models
- **Random Forest**: Non-linear relationship detection
- **Neural Networks**: Complex pattern recognition
- **Support Vector Machines**: Classification and regression

### Spatial Analysis
- **Moran's I**: Spatial autocorrelation
- **Getis-Ord Gi***: Hot spot analysis
- **Buffer Analysis**: 5km zones around industries/mines

## Deployment Guide

### Prerequisites
- Docker and Docker Compose
- At least 8GB RAM
- 50GB free disk space

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd HealthTrace

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Service URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Kafka UI**: http://localhost:9000

### Production Deployment
1. Update environment variables in `docker-compose.yml`
2. Configure SSL certificates in `deployment/ssl/`
3. Update Nginx configuration
4. Set up monitoring and logging
5. Configure backup strategies

## User Roles and Permissions

### Role Hierarchy
1. **Admin**: Full system access
2. **U.O.C. Epidemiology**: Complete monitoring and analytics
3. **U.O.S.D.**: Epidemiological investigations
4. **MMG/PLS**: Disease reporting only

### Permission Matrix
| Feature | Admin | U.O.C. Epidemiology | U.O.S.D. | MMG/PLS |
|---------|-------|---------------------|----------|---------|
| User Management | ✓ | - | - | - |
| Disease Reporting | ✓ | ✓ | - | ✓ |
| Patient Management | ✓ | ✓ | ✓ | ✓ |
| Epidemiological Investigations | ✓ | ✓ | ✓ | - |
| Analytics Dashboard | ✓ | ✓ | - | - |
| Environmental Data | ✓ | ✓ | - | - |
| Geo Visualization | ✓ | ✓ | - | - |

## Legal Compliance

### Legal Limits (Section 1.3)
The system monitors compliance with:

| Pollutant | Legal Limit | Reference | WHO Recommendation |
|-----------|-------------|-----------|-------------------|
| CO | 10 mg/m³ | Legislative Decree 155/2010 | - |
| Benzene | 5 μg/m³ | Legislative Decree 155/2010 | - |
| SO₂ | 125 μg/m³ | Legislative Decree 155/2010 | - |
| PM10 | 50 μg/m³ | Legislative Decree 155/2010 | 50 μg/m³ (3x/year) |
| PM2.5 | 25 μg/m³ | Legislative Decree 155/2010 | 10 μg/m³ |
| Ozone | 180 μg/m³ | Legislative Decree 155/2010 | - |
| NO₂ | 200 μg/m³ | Legislative Decree 155/2010 | 30 μg/m³ (annual) |

### Data Privacy
- GDPR compliance for patient data
- Anonymization options for research
- Audit trails for data access
- Secure data transmission

## Correlation Analysis

### Disease-Environment Correlations (Section 1.4)

#### Respiratory Diseases
- **Primary Factors**: PM10, PM2.5, NO₂, SO₂
- **Mechanism**: Airway damage, immune compromise
- **Diseases**: Influenza, Legionellosis

#### Airborne Infections
- **Primary Factors**: PM10, PM2.5 (transport vectors)
- **Diseases**: Measles, Rubella, Encephalitis, Meningitis

#### Vector-Borne Diseases
- **Primary Factors**: Temperature, Humidity, Rainfall
- **Diseases**: Malaria, Dengue, Chikungunya, Zika

#### Waterborne Diseases
- **Primary Factors**: Water pollution, extreme weather events
- **Diseases**: Cholera, Typhoid, Hepatitis A

#### Zoonotic Diseases
- **Primary Factors**: Vector density, habitat destruction
- **Diseases**: Plague, Lyme Disease

### Regional Focus
The system specifically targets:
- **Molise**: Industrial pollution monitoring
- **Campania**: Urban air quality correlation
- **Calabria**: Agricultural and coastal factors

This documentation provides a comprehensive guide to the HealthTrace system, covering all technical aspects from architecture to deployment.
