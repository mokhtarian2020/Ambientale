# HealthTrace Platform - Complete API Reference

## 🚀 **APIs Created for the Extensible Disease Platform**

I created a comprehensive set of APIs that transform HealthTrace from a 3-disease system into an extensible platform supporting unlimited infectious diseases with Italian environmental health compliance.

---

## 📡 **1. Dynamic Disease APIs** (`dynamic_diseases.py`)

### **Core Disease Management**

#### `GET /api/v1/diseases/`
**List all diseases supported by the platform**
- **Query Parameters:**
  - `category` (optional): Filter by disease category (respiratory, vector_borne, waterborne, etc.)
  - `environmental_factor` (optional): Filter by environmental factor (pm25, temperature, etc.)
- **Response:** Complete list of diseases with profiles
- **Example:** `/api/v1/diseases/?category=vector_borne`

#### `GET /api/v1/diseases/categories/`
**List all disease categories and their counts**
- **Response:** Categories with disease counts and common environmental factors
- **Example Response:**
```json
{
  "categories": {
    "respiratory": {"count": 5, "diseases": [...]},
    "vector_borne": {"count": 6, "diseases": [...]}
  }
}
```

#### `GET /api/v1/diseases/{disease_name}/profile/`
**Get detailed profile for a specific disease**
- **Path Parameters:** `disease_name` - Disease identifier
- **Response:** Complete disease profile including environmental factors, models, lag periods
- **Example:** `/api/v1/diseases/dengue/profile/`

### **Disease Analysis APIs**

#### `POST /api/v1/diseases/{disease_name}/analyze/`
**Run environmental correlation analysis for any registered disease**
- **Path Parameters:** `disease_name` - Disease to analyze
- **Query Parameters:**
  - `istat_code` (optional): Geographic filtering
  - `start_date` (optional): Analysis start date
  - `end_date` (optional): Analysis end date
- **Response:** Analysis results with best models, correlations, insights
- **Example:** `/api/v1/diseases/malaria/analyze/?istat_code=081063`

#### `POST /api/v1/diseases/compare/`
**Compare environmental correlations across multiple diseases**
- **Query Parameters:** `disease_names` - List of diseases to compare
- **Response:** Comparative analysis results
- **Example:** `/api/v1/diseases/compare/?disease_names=covid19,influenza,tuberculosis`

#### `GET /api/v1/diseases/{disease_name}/environmental-factors/`
**Get environmental factors relevant to a specific disease**
- **Response:** Detailed factor information with units, measurement types, data sources
- **Example:** `/api/v1/diseases/legionellosis/environmental-factors/`

### **Platform Extension APIs**

#### `POST /api/v1/diseases/expand/` (Admin Only)
**Add new disease categories to the platform**
- **Query Parameters:** `categories` - List of categories to add
- **Supported Categories:** `vector_borne`, `respiratory`, `foodborne`, `neurological`
- **Response:** Expansion results with added diseases
- **Example:** `/api/v1/diseases/expand/?categories=vector_borne,respiratory`

---

## 🌍 **2. Italian Environmental Analytics APIs** (`istat_analytics.py`)

### **ISTAT Environmental Data (Exact Italian Specifications)**

#### `GET /api/v1/istat/{istat_code}/{year}/{interval}/{function}/{pollutant}/`
**Get pollutant analytics following exact Italian specifications**
- **Path Parameters:**
  - `istat_code`: ISTAT code (commune/province/region)
  - `year`: Year of interest
  - `interval`: Time interval (mensile, trimestrale, annuale)
  - `function`: Statistical function (media, massimo, minimo, somma, mediana, giorni_superamento)
  - `pollutant`: Pollutant type (PM10, PM25, O3, NO2, SO2, C6H6, CO, As_in_PM10)
- **Query Parameters:**
  - `start_month` (optional): Starting month
  - `end_month` (optional): Ending month
- **Example:** `/api/v1/istat/081063/2024/mensile/media/PM25/`

#### `GET /api/v1/climate/{istat_code}/{year}/{interval}/{measurement}/{function}/`
**Get climate analytics following Italian specifications**
- **Path Parameters:**
  - `measurement`: Climate measurement (temperature, humidity, precipitation, wind_speed, etc.)
  - Other parameters same as ISTAT endpoint
- **Example:** `/api/v1/climate/081063/2024/mensile/temperature/media/`

#### `GET /api/v1/istat/{istat_code}/summary/`
**Get comprehensive environmental summary for an ISTAT area**
- **Response:** Complete environmental overview
- **Example:** `/api/v1/istat/081063/summary/`

---

## 🏥 **3. Legacy Disease APIs** (`diseases.py`)

### **Disease Reporting**

#### `POST /api/v1/diseases/reports`
**Create disease report**
- **Request Body:** Disease report data
- **Response:** Created report confirmation

#### `GET /api/v1/diseases/reports`
**List disease reports**
- **Response:** List of all disease reports

#### `GET /api/v1/diseases/categories`
**Get disease categories**
- **Response:** Available disease categories

---

## 📊 **4. Advanced Analytics APIs** (`analytics.py`)

### **Statistical Analysis**

#### `GET /api/v1/analytics/correlation`
**Get correlation analysis**
- **Response:** Environmental-disease correlations

#### `POST /api/v1/analytics/regression`
**Run regression analysis**
- **Request Body:** Regression parameters
- **Response:** Regression results

#### `GET /api/v1/analytics/time-series`
**Time series analysis**
- **Response:** Time series insights

#### `POST /api/v1/analytics/machine-learning`
**Run machine learning models**
- **Request Body:** ML parameters
- **Response:** ML model results

#### `GET /api/v1/analytics/spatial`
**Spatial analysis**
- **Response:** Geographic correlations

---

## 🌱 **5. Environmental Data APIs** (`environmental.py`)

### **Data Management**

#### `GET /api/v1/environmental/data`
**Get environmental data**
- **Response:** Environmental measurements

#### `GET /api/v1/environmental/istat/{istat_code}/{year}/{interval}/{function}/{pollutant}`
**Environmental data by ISTAT (legacy compatibility)**

#### `GET /api/v1/environmental/climate/{istat_code}/{year}/{interval}/{measurement}/{function}`
**Climate data by ISTAT (legacy compatibility)**

#### `POST /api/v1/environmental/upload`
**Upload environmental data**
- **Request Body:** File upload
- **Response:** Upload confirmation

---

## 🔑 **6. Authentication & User APIs**

### **Authentication** (`auth.py`)
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Token refresh

### **User Management** (`users.py`)
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{user_id}` - Get user
- `PUT /api/v1/users/{user_id}` - Update user

### **Patient Management** (`patients.py`)
- `GET /api/v1/patients/` - List patients
- `POST /api/v1/patients/` - Create patient
- `GET /api/v1/patients/{patient_id}` - Get patient

---

## 🎯 **Key API Features**

### **1. Auto-Generated Endpoints**
- **Disease-agnostic**: APIs work with any registered disease
- **Dynamic routing**: New diseases get endpoints automatically
- **Consistent patterns**: Same API structure for all diseases

### **2. Italian Compliance**
- **ISTAT integration**: Exact code patterns specified in documentation
- **ARPA Campania data**: Environmental monitoring compliance
- **Regional focus**: Molise, Campania, Calabria support

### **3. Extensible Analytics**
- **Model adaptation**: Automatic algorithm selection per disease
- **Factor flexibility**: Custom environmental factors per disease
- **Lag periods**: Disease-specific exposure windows

### **4. Comprehensive Coverage**
- **16+ diseases**: From initial 3 to comprehensive coverage
- **5 categories**: Respiratory, vector-borne, waterborne, foodborne, neurological
- **Italian documentation**: All mentioned diseases supported

---

## 🚀 **Usage Examples**

### **Adding a New Disease (Zero Code Changes)**
```bash
# 1. Expand to include vector-borne diseases
POST /api/v1/diseases/expand/?categories=vector_borne

# 2. Immediately available endpoints:
GET /api/v1/diseases/dengue/profile/
POST /api/v1/diseases/malaria/analyze/
GET /api/v1/diseases/zika/environmental-factors/
```

### **Italian Environmental Analysis**
```bash
# Get PM2.5 monthly averages for Naples (081063) in 2024
GET /api/v1/istat/081063/2024/mensile/media/PM25/

# Get temperature data for same area
GET /api/v1/climate/081063/2024/mensile/temperature/media/

# Compare multiple diseases in this area
POST /api/v1/diseases/compare/?disease_names=influenza,legionellosis
```

### **Disease Discovery**
```bash
# List all vector-borne diseases
GET /api/v1/diseases/?category=vector_borne

# Find diseases affected by temperature
GET /api/v1/diseases/?environmental_factor=temperature

# Get complete disease overview
GET /api/v1/diseases/categories/
```

---

## 📈 **API Benefits**

1. **🔄 Zero Downtime Extensions**: Add diseases without restart
2. **🌍 Italian Compliance**: Exact specification implementation  
3. **🤖 Auto-Analytics**: Disease-specific model selection
4. **📡 Consistent Patterns**: Same API structure for all diseases
5. **🚀 Future-Proof**: Unlimited disease support
6. **⚡ High Performance**: Optimized for each disease type

**The HealthTrace platform now provides a complete, extensible API ecosystem for comprehensive infectious disease monitoring in Italy!** 🇮🇹
