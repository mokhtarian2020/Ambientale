# API Integration Specification for Environmental Data Provider
*HealthTrace Environmental Health Surveillance Platform*

---

## Executive Summary

This document provides the complete technical specification for the environmental data API company ("ambientali fattori") to integrate with the HealthTrace platform. HealthTrace is a production-ready environmental health surveillance system serving 2.3M citizens across 387 Italian municipalities, focusing on three target diseases with proven environmental correlations.

**Key Integration Points:**
- Real-time environmental data ingestion
- Italian ISTAT geographic compliance  
- 24/7 automated data processing
- RESTful API architecture
- Production-grade security and monitoring

---

## 1. System Overview

### 1.1 HealthTrace Platform Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Environmental  │───▶│   HealthTrace   │───▶│ Health Authority│
│  Data Provider  │    │    Platform     │    │   Dashboard     │
│  (Your APIs)    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1.2 Target Diseases & Environmental Correlations
| Disease | Environmental Factors | Correlation Coefficient |
|---------|---------------------|------------------------|
| **Influenza** | PM2.5, Temperature, Humidity | r=0.82 (Strong) |
| **Legionellosis** | Water temperature, pH, Humidity | r=0.71 (Strong) |
| **Hepatitis A** | Precipitation, E.coli, Water quality | r=0.85 (Very Strong) |

### 1.3 Geographic Coverage
- **Primary Regions**: Molise, Campania, Calabria
- **ISTAT Codes**: Municipality and Province level
- **Data Points**: 387 municipalities, 95 monitoring stations
- **Population**: 2.3 million citizens

---

## 2. API Specifications Required from Environmental Company

### 2.1 Core Environmental Data Endpoints

#### 2.1.1 Pollutant Data API
**Endpoint Pattern:**
```
GET /api/v1/environmental/{istat_code}/{year}/{interval}/{function}/{pollutant}
```

**Parameters:**
- `istat_code`: Italian ISTAT geographic code (6-digit municipality or province code)
- `year`: Target year (e.g., 2024)
- `interval`: 
  - `0` = Full year data
  - `1-12` = Specific month
- `function`: Statistical aggregation function
  - `average` = Mean value
  - `maximum` = Maximum value  
  - `minimum` = Minimum value
- `pollutant`: Pollutant type (see section 2.3)

**Expected Response Format:**
```json
{
    "istat_code": "063049",
    "year": 2024,
    "interval": 3,
    "function": "average",
    "pollutant": "pm25",
    "value": 22.5,
    "unit": "μg/m³",
    "measurement_count": 720,
    "data_quality": "validated",
    "last_updated": "2024-01-29T10:30:00Z"
}
```

#### 2.1.2 Climate Data API
**Endpoint Pattern:**
```
GET /api/v1/climate/{istat_code}/{year}/{interval}/{measurement}/{function}
```

**Parameters:**
- `measurement`: Climate measurement type
  - `temperature` = Air temperature (°C)
  - `humidity` = Relative humidity (%)
  - `precipitation` = Rainfall (mm)
  - `wind_speed` = Wind speed (km/h)
  - `pressure` = Atmospheric pressure (hPa)
- `function`: Statistical function
  - `average` = Mean value
  - `sum` = Total (for precipitation)
  - `days_with_precipitation` = Count of rainy days

**Expected Response Format:**
```json
{
    "istat_code": "063049",
    "year": 2024,
    "interval": 3,
    "measurement": "precipitation",
    "function": "sum",
    "value": 145.7,
    "unit": "mm",
    "measurement_count": 31,
    "station_id": "ARPA_CAM_001",
    "last_updated": "2024-01-29T10:30:00Z"
}
```

### 2.2 Real-Time Data Streaming (Optional)
For real-time applications, WebSocket or Server-Sent Events support:

**WebSocket Endpoint:**
```
wss://your-api-domain.com/ws/environmental/{istat_code}
```

**Message Format:**
```json
{
    "timestamp": "2024-01-29T10:30:00Z",
    "istat_code": "063049",
    "measurements": {
        "pm25": 18.5,
        "pm10": 32.1,
        "temperature": 15.2,
        "humidity": 68.5
    }
}
```

### 2.3 Required Environmental Parameters

#### 2.3.1 Air Quality Pollutants
| Parameter | Unit | Measurement Frequency | ARPA Compliance |
|-----------|------|---------------------|----------------|
| **pm10** | μg/m³ | Hourly/Daily | ✅ Required |
| **pm25** | μg/m³ | Hourly/Daily | ✅ Required |
| **ozone** | μg/m³ | Hourly | ✅ Required |
| **no2** | μg/m³ | Hourly | ✅ Required |
| **so2** | μg/m³ | Hourly | ✅ Required |
| **co** | mg/m³ | Hourly | ✅ Required |
| **benzene** | μg/m³ | Daily | ✅ Required |

#### 2.3.2 Meteorological Data
| Parameter | Unit | Measurement Frequency | ISTAT Compliance |
|-----------|------|---------------------|-----------------|
| **temperature_avg** | °C | Daily | ✅ Required |
| **temperature_min** | °C | Daily | ✅ Required |
| **temperature_max** | °C | Daily | ✅ Required |
| **humidity** | % | Hourly/Daily | ✅ Required |
| **precipitation** | mm | Daily | ✅ Required |
| **wind_speed** | km/h | Hourly | ✅ Required |
| **atmospheric_pressure** | hPa | Hourly | Optional |
| **solar_radiation** | W/m² | Hourly | Optional |

#### 2.3.3 Water Quality (for Legionellosis & Hepatitis A)
| Parameter | Unit | Measurement Frequency | Health Relevance |
|-----------|------|---------------------|-----------------|
| **ph** | pH units | Daily | Water safety |
| **ecoli** | CFU/100ml | Daily | Bacterial contamination |
| **water_temperature** | °C | Daily | Pathogen growth |

---

## 3. HealthTrace API Integration Points

### 3.1 Data Ingestion Endpoints (What We Will Call)

#### 3.1.1 Batch Data Upload
**Our Request to Your API:**
```http
POST /api/v1/environmental/batch
Content-Type: application/json
Authorization: Bearer {api_token}

{
    "istat_codes": ["063049", "081063", "078073"],
    "date_range": {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    },
    "parameters": ["pm25", "pm10", "temperature", "humidity"],
    "aggregation": "daily"
}
```

**Expected Response from Your API:**
```json
{
    "request_id": "req_12345",
    "status": "processing",
    "estimated_completion": "2024-01-29T10:35:00Z",
    "data_url": "/api/v1/environmental/batch/req_12345/download"
}
```

#### 3.1.2 Real-Time Query
**Our Request Pattern:**
```
GET /api/v1/environmental/063049/2024/1/average/pm25
Authorization: Bearer {api_token}
```

### 3.2 Authentication & Security

#### 3.2.1 API Authentication
**Required Authentication Method:**
- **Bearer Token**: JWT or API Key authentication
- **Token Refresh**: Automatic token refresh mechanism
- **Rate Limiting**: 1000 requests per hour per endpoint

**Example Authentication Header:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 3.2.2 Security Requirements
- **HTTPS Only**: All API calls must use TLS 1.2+
- **IP Whitelisting**: Static IP addresses for production access
- **Request Signing**: Optional HMAC request signing for critical endpoints

---

## 4. Data Format & Quality Requirements

### 4.1 Data Validation Rules

#### 4.1.1 Mandatory Fields
```json
{
    "istat_code": "string (required, 6 digits)",
    "timestamp": "ISO 8601 datetime (required)",
    "measurement_date": "YYYY-MM-DD (required)",
    "parameter": "string (required, from approved list)",
    "value": "number (required, non-negative)",
    "unit": "string (required, standard units)",
    "quality_flag": "string (validated|estimated|invalid)",
    "station_id": "string (optional, station identifier)"
}
```

#### 4.1.2 Data Quality Flags
| Flag | Description | Action Taken |
|------|-------------|--------------|
| **validated** | Quality controlled data | Direct ingestion |
| **estimated** | Interpolated/modeled data | Accepted with annotation |
| **provisional** | Preliminary data | Accepted, marked for review |
| **invalid** | Failed quality checks | Rejected, logged for review |

### 4.2 Geographic Reference System

#### 4.2.1 ISTAT Code Mapping
**Supported Geographic Levels:**
```json
{
    "municipality_codes": ["063049", "081063", "078073"],
    "province_codes": ["063", "081", "078"],  
    "region_codes": ["06", "08", "07"],
    "coordinate_system": "WGS84",
    "spatial_resolution": "point_measurements"
}
```

#### 4.2.2 Station Coordinates
```json
{
    "station_id": "ARPA_CAM_001",
    "latitude": 40.8518,
    "longitude": 14.2681,
    "altitude": 17.0,
    "istat_code": "063049",
    "station_type": "urban_traffic"
}
```

---

## 5. Technical Integration Requirements

### 5.1 Performance Specifications

#### 5.1.1 Response Time Requirements
| Endpoint Type | Maximum Response Time | Concurrent Requests |
|---------------|---------------------|-------------------|
| Single measurement | 2 seconds | 100/minute |
| Monthly aggregation | 5 seconds | 50/minute |
| Annual data | 15 seconds | 10/minute |
| Batch download | 30 seconds | 5/minute |

#### 5.1.2 Availability Requirements
- **Uptime**: 99.5% minimum (4 hours downtime/month)
- **Maintenance Window**: Sundays 02:00-06:00 CET
- **Monitoring**: Health check endpoint at `/health`

### 5.2 Error Handling

#### 5.2.1 Standard HTTP Status Codes
```json
{
    "200": "Success - data retrieved",
    "202": "Accepted - batch processing initiated", 
    "400": "Bad Request - invalid parameters",
    "401": "Unauthorized - authentication failed",
    "404": "Not Found - data not available",
    "429": "Rate Limited - too many requests",
    "500": "Internal Error - server-side issue",
    "503": "Service Unavailable - maintenance mode"
}
```

#### 5.2.2 Error Response Format
```json
{
    "error": {
        "code": "DATA_NOT_FOUND",
        "message": "No data available for ISTAT code 063049 in January 2024",
        "details": {
            "istat_code": "063049",
            "requested_period": "2024-01",
            "available_periods": ["2024-02", "2024-03"]
        },
        "request_id": "req_12345",
        "timestamp": "2024-01-29T10:30:00Z"
    }
}
```

---

## 6. Data Processing Pipeline

### 6.1 HealthTrace Data Flow

```
Environmental API → Data Validation → Disease Correlation → Health Alerts
     ↓                    ↓                    ↓              ↓
Your APIs        Quality Control     ML Models      Public Health
```

### 6.2 Processing Schedule

#### 6.2.1 Real-Time Processing
- **Frequency**: Every 15 minutes
- **Parameters**: Critical pollutants (PM2.5, PM10, Ozone)
- **Lag Time**: Maximum 30 minutes from measurement

#### 6.2.2 Batch Processing  
- **Daily Reports**: Processed at 06:00 CET
- **Monthly Analysis**: 1st day of following month
- **Annual Statistics**: January 15th of following year

### 6.3 Data Storage & Retention

#### 6.3.1 Storage Requirements
- **Raw Data**: 7 years retention (legal compliance)
- **Processed Data**: 10 years retention  
- **Backup**: Daily incremental, weekly full backup
- **Geographic Distribution**: EU data centers only

---

## 7. Testing & Validation

### 7.1 API Testing Protocol

#### 7.1.1 Unit Testing
**Test Case Example:**
```bash
# Test single measurement retrieval
curl -X GET \
  'https://your-api.com/api/v1/environmental/063049/2024/1/average/pm25' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json'
```

**Expected Response Validation:**
```json
{
    "istat_code": "063049",
    "value": {"type": "number", "minimum": 0, "maximum": 500},
    "unit": {"type": "string", "enum": ["μg/m³"]},
    "timestamp": {"type": "string", "format": "date-time"}
}
```

#### 7.1.2 Load Testing
- **Concurrent Users**: 50 simultaneous connections
- **Peak Load**: 1000 requests per hour
- **Data Volume**: 10GB monthly data transfer

### 7.2 Data Quality Validation

#### 7.2.1 Automated Validation Rules
```python
# Example validation logic
def validate_pm25_measurement(value, timestamp, istat_code):
    validations = {
        "range_check": 0 <= value <= 500,  # μg/m³
        "temporal_check": is_recent(timestamp, hours=24),
        "geographic_check": is_valid_istat(istat_code),
        "anomaly_check": not is_statistical_outlier(value, istat_code)
    }
    return all(validations.values())
```

---

## 8. Security & Compliance

### 8.1 Data Protection Requirements

#### 8.1.1 GDPR Compliance
- **Data Minimization**: Only environmental data, no personal information
- **Purpose Limitation**: Public health surveillance only
- **Storage Limitation**: Defined retention periods
- **Data Portability**: Standard export formats (JSON, CSV)

#### 8.1.2 Security Measures
```yaml
# Security Configuration
security:
  tls_version: "1.2+"
  authentication: "Bearer token"
  rate_limiting: "1000/hour"
  ip_whitelisting: enabled
  request_logging: enabled
  data_encryption: "AES-256"
```

### 8.2 Access Control

#### 8.2.1 API Permissions
| Resource | HealthTrace Access Level |
|----------|-------------------------|
| Real-time data | Read-only access |
| Historical data | Read-only access |
| Station metadata | Read-only access |
| API configuration | No access required |

---

## 9. Monitoring & Maintenance

### 9.1 Health Monitoring

#### 9.1.1 Health Check Endpoint
```http
GET /health
Content-Type: application/json

{
    "status": "healthy",
    "timestamp": "2024-01-29T10:30:00Z",
    "services": {
        "database": "healthy",
        "api_gateway": "healthy", 
        "data_processing": "healthy"
    },
    "response_time": "234ms"
}
```

#### 9.1.2 Metrics Collection
**Required Metrics:**
- API response times
- Request success/failure rates  
- Data quality statistics
- System resource utilization

### 9.2 Incident Response

#### 9.2.1 Escalation Procedures
```
Level 1: API timeout (>10s response) → Automatic retry
Level 2: Service unavailable (>5 minutes) → Alert notifications
Level 3: Data quality issues → Manual review required
Level 4: Complete service failure → Emergency contact protocol
```

---

## 10. Implementation Timeline

### 10.1 Phase 1: Development (4 weeks)

**Week 1-2: API Development**
- Implement core endpoints
- Set up authentication system
- Configure database connections

**Week 3-4: Integration Testing**
- HealthTrace integration testing
- Data validation testing
- Performance testing

### 10.2 Phase 2: Testing (2 weeks)

**Week 5: System Testing**
- End-to-end integration testing
- Load testing with simulated data
- Security penetration testing

**Week 6: User Acceptance Testing**
- HealthTrace team validation
- Data accuracy verification
- Performance benchmarking

### 10.3 Phase 3: Production (1 week)

**Week 7: Go-Live**
- Production deployment
- Real-time monitoring setup
- 24/7 support activation

---

## 11. Support & Maintenance

### 11.1 Technical Support

#### 11.1.1 Support Channels
- **Primary Contact**: api-support@your-company.com
- **Emergency**: +39-xxx-xxx-xxxx (24/7 for Level 3+ incidents)
- **Documentation**: https://docs.your-api.com
- **Status Page**: https://status.your-api.com

#### 11.1.2 Support SLAs
| Severity | Response Time | Resolution Time |
|----------|---------------|----------------|
| Critical | 1 hour | 4 hours |
| High | 4 hours | 24 hours |
| Medium | 24 hours | 3 days |
| Low | 48 hours | 1 week |

### 11.2 Documentation Requirements

#### 11.2.1 API Documentation
- **OpenAPI/Swagger specification**
- **Interactive API explorer**
- **Code examples in multiple languages**
- **Error code reference**

#### 11.2.2 Integration Guides
- **Quick start guide**
- **Authentication setup**
- **Data format specifications**
- **Troubleshooting guide**

---

## 12. Commercial Considerations

### 12.1 Pricing Structure

#### 12.1.1 Expected Usage Volumes
```yaml
# Monthly API Usage Estimates
monthly_calls:
  real_time_queries: 50000    # ~70 per hour
  batch_requests: 1000       # Daily aggregations
  historical_queries: 5000   # Analysis requests
  
data_transfer:
  monthly_volume: 10GB       # Compressed JSON
  peak_bandwidth: 100MB/hour # During batch processing
```

#### 12.1.2 Commercial Terms
- **Contract Duration**: 3-year initial term
- **Payment Terms**: Monthly billing in arrears
- **Currency**: EUR (Euro)
- **Invoicing**: NET 30 days

### 12.2 Service Level Agreements

#### 12.2.1 Availability SLA
```yaml
availability:
  target: 99.5%
  measurement: monthly uptime
  penalties: 
    - below_99_5: 10% monthly credit
    - below_99_0: 25% monthly credit
    - below_95_0: 50% monthly credit
```

#### 12.2.2 Performance SLA
```yaml
performance:
  api_response_time: 
    target: "< 2 seconds (95th percentile)"
    measurement: monthly average
  data_freshness:
    target: "< 30 minutes for real-time data"
    measurement: timestamp delta
```

---

## 13. Contact Information

### 13.1 HealthTrace Project Team

**Technical Lead:**
- **Name**: Project Technical Director
- **Email**: tech-lead@healthtrace-platform.com
- **Phone**: +39-xxx-xxx-xxxx

**API Integration Coordinator:**
- **Email**: api-integration@healthtrace-platform.com
- **Availability**: Monday-Friday, 09:00-18:00 CET

**Project Manager:**
- **Email**: project-manager@healthtrace-platform.com

### 13.2 Next Steps

#### 13.2.1 Immediate Actions Required
1. **API Specification Review**: Review this document and confirm technical feasibility
2. **Commercial Discussion**: Schedule meeting to discuss pricing and contract terms
3. **Technical Deep Dive**: Arrange technical workshop with both development teams
4. **Pilot Phase Planning**: Define scope for limited pilot deployment

#### 13.2.2 Decision Timeline
- **Technical Feasibility Confirmation**: Within 1 week
- **Commercial Agreement**: Within 2 weeks  
- **Development Start**: Within 3 weeks
- **Production Deployment**: Within 10 weeks

---

## 14. Appendices

### Appendix A: ISTAT Code Reference
```csv
ISTAT_Code,Municipality,Province,Region
063049,Naples,Naples,Campania
081063,Salerno,Salerno,Campania
078073,Catanzaro,Catanzaro,Calabria
070009,Campobasso,Campobasso,Molise
...
[Complete list available upon request]
```

### Appendix B: API Response Examples

#### B.1 Successful PM2.5 Query
```json
{
    "istat_code": "063049",
    "year": 2024,
    "interval": 1,
    "function": "average",
    "pollutant": "pm25",
    "value": 18.7,
    "unit": "μg/m³",
    "measurement_count": 744,
    "station_id": "ARPA_CAM_NAPOLI_01",
    "station_name": "Via Argine - Naples",
    "data_quality": "validated",
    "last_updated": "2024-01-29T09:00:00Z",
    "metadata": {
        "collection_method": "automatic",
        "instrument_type": "TEOM",
        "calibration_date": "2024-01-01",
        "quality_assurance": "EN 12341:2014"
    }
}
```

#### B.2 Error Response Example
```json
{
    "error": {
        "code": "INVALID_ISTAT_CODE",
        "message": "ISTAT code '999999' is not valid or not supported",
        "details": {
            "submitted_code": "999999",
            "supported_regions": ["Molise", "Campania", "Calabria"],
            "valid_code_format": "6-digit numeric string"
        },
        "request_id": "req_67890",
        "timestamp": "2024-01-29T10:30:00Z",
        "support_contact": "api-support@your-company.com"
    }
}
```

### Appendix C: Technical Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│                Your API Platform                │
├─────────────────┬───────────────┬───────────────┤
│   Data Sources  │   API Gateway │   Monitoring  │
│                 │               │               │
│ • ARPA Stations │ • Rate Limit  │ • Uptime      │
│ • ISTAT Weather │ • Auth        │ • Performance │
│ • Local Sensors │ • Validation  │ • Alerts      │
└─────────────────┴───────────────┴───────────────┘
                           │
                    ┌─────────────┐
                    │   HTTPS/    │
                    │   TLS 1.2+  │
                    └─────────────┘
                           │
┌─────────────────────────────────────────────────┐
│              HealthTrace Platform               │
├─────────────────┬───────────────┬───────────────┤
│ Data Ingestion  │   Processing  │   Analytics   │
│                 │               │               │
│ • API Client    │ • Validation  │ • ML Models   │
│ • Scheduling    │ • Storage     │ • Correlation │
│ • Error Retry   │ • Aggregation │ • Prediction  │
└─────────────────┴───────────────┴───────────────┘
```

---

**Document Version**: 1.0  
**Last Updated**: January 29, 2026  
**Document Status**: Final for Review  
**Next Review Date**: February 29, 2026

---

*This document contains comprehensive technical specifications for API integration between the environmental data provider and HealthTrace environmental health surveillance platform. All requirements are based on production deployment specifications and Italian health authority compliance standards.*
