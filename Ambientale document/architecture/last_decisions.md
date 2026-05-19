# HealthTrace Data Architecture – Project Constraints
## 1. Data Sources
External environmental data is provided by ARPES through:
APIs or
read-only database access
ARPES systems are considered data sources only.
Our platform must not depend directly on their operational database for analytics.

# 2. Two Data Processing Pipelines
The system is designed with two independent flows.

# Pipeline 1 – Analytical Pipeline
Purpose:
dashboards
spatial analysis
epidemiological correlations
forecasting models
reporting
Flow:

ARPES (API / DB source)
↓
Data ingestion / ETL
↓
Data Warehouse (DWH)
↓
BI tools (Superset)

Characteristics:
batch processing
scheduled ingestion jobs (e.g. cron)
ETL performs:
data cleaning
normalization
aggregation
integration with other datasets
The Data Warehouse is the central system for analytics.

# Pipeline 2 – Rapid Monitoring / Alert Pipeline
Purpose:
real-time monitoring
anomaly detection
threshold alerts
early warning indicators
Flow:

Data stream
↓
Kafka
↓
Consumer service
↓
Alert engine

Characteristics:
near real-time processing
independent from the DWH for immediate decisions
consumers perform:
threshold checks
anomaly detection
preliminary analysis
Generated alerts may later be stored in the DWH for:
historical analysis
audit logs
alert dashboards

# 3. Role of the Data Warehouse
The DWH is used for:
historical storage
analytical queries
integration of multiple datasets
dashboards and reporting
ML model training
It must not be required for real-time alert decisions.

# 4. ETL Layer
The ETL / ingestion layer is responsible for:
extracting data from ARPES APIs or DB
validating and cleaning data
transforming schema
computing aggregates
loading data into the DWH
ETL jobs may run:
periodically (cron)
or via ETL tools

# 5. Real-Time Processing Layer
Real-time monitoring is implemented through:

Kafka → Consumer → Alert Logic

Responsibilities:
process incoming streams
detect anomalies
generate alerts
optionally store alert events in DWH

# 6. BI and Visualization
Analytics and dashboards are implemented using:

Superset

Connected directly to the Data Warehouse.

# 7. High-Level Architecture

┌─────────────────┐
│     ARPES       │
│  API / DB data  │
└─────────┬───────┘
│
Ingestion / ETL
│
Data Warehouse
│
Superset
(Dashboards / BI)
Real-time monitoring pipeline
Data Streams
│
Kafka
│
Consumer
│
Alert Engine
│
(optional) store alerts
│
Data Warehouse

