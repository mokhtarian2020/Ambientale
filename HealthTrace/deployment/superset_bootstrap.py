"""
Superset Bootstrap Script
==========================
Run ONCE after the Superset container starts to:
  1. Register the HealthTrace DWH PostgreSQL database connection
  2. Register the GESAN malattie infettive PostgreSQL connection
  3. Create the core datasets (virtual tables / saved queries)
  4. Create starter charts and a default dashboard

Usage (from host or inside container):
    docker exec healthtrace_superset python /app/pythonpath/superset_bootstrap.py

Or directly:
    python deployment/superset_bootstrap.py \
        --superset-url http://localhost:8088 \
        --username admin --password admin
"""

import argparse
import json
import logging
import sys
from typing import Any, Dict, Optional

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class SupersetClient:
    def __init__(self, base_url: str, username: str, password: str):
        self._base = base_url.rstrip("/")
        self._session = requests.Session()
        self._login(username, password)

    def _login(self, username: str, password: str) -> None:
        # Get CSRF token
        resp = self._session.get(f"{self._base}/api/v1/security/csrf_token/")
        csrf = resp.json().get("result", "")
        self._session.headers["X-CSRFToken"] = csrf

        resp = self._session.post(
            f"{self._base}/api/v1/security/login",
            json={"username": username, "password": password, "provider": "db", "refresh": True},
        )
        resp.raise_for_status()
        token = resp.json()["access_token"]
        self._session.headers["Authorization"] = f"Bearer {token}"
        logger.info("Logged in to Superset as %s", username)

    def post(self, path: str, body: Dict) -> Dict:
        resp = self._session.post(f"{self._base}{path}", json=body)
        if resp.status_code not in (200, 201):
            logger.warning("POST %s → %d: %s", path, resp.status_code, resp.text[:200])
        return resp.json()

    def get_existing_ids(self, path: str, name_field: str = "database_name") -> Dict[str, int]:
        resp = self._session.get(f"{self._base}{path}?q=(page_size:200)")
        if resp.status_code != 200:
            return {}
        return {item[name_field]: item["id"] for item in resp.json().get("result", [])}


def register_databases(client: SupersetClient) -> Dict[str, int]:
    """Register HealthTrace DWH and GESAN databases in Superset."""
    existing = client.get_existing_ids("/api/v1/database/")

    databases = [
        {
            "database_name": "HealthTrace DWH",
            "sqlalchemy_uri": "postgresql+psycopg2://healthtrace:healthtrace_password@database:5432/healthtrace",
            "expose_in_sqllab": True,
            "allow_run_async": True,
            "extra": json.dumps({
                "metadata_params": {},
                "engine_params": {},
                "schemas_allowed_for_file_upload": ["public"],
            }),
        },
        {
            "database_name": "GESAN Malattie Infettive",
            "sqlalchemy_uri": "postgresql+psycopg2://readonly:readonly@10.10.13.11:5432/gesan_malattieinfettive",
            "expose_in_sqllab": True,
            "allow_run_async": True,
        },
    ]

    db_ids: Dict[str, int] = {}
    for db in databases:
        if db["database_name"] in existing:
            db_ids[db["database_name"]] = existing[db["database_name"]]
            logger.info("Database already registered: %s (id=%d)", db["database_name"], db_ids[db["database_name"]])
            continue
        result = client.post("/api/v1/database/", db)
        db_id = result.get("id")
        if db_id:
            db_ids[db["database_name"]] = db_id
            logger.info("Registered database: %s (id=%d)", db["database_name"], db_id)
        else:
            logger.warning("Failed to register database: %s", db["database_name"])

    return db_ids


def register_datasets(client: SupersetClient, dwh_db_id: int) -> Dict[str, int]:
    """Create virtual datasets (saved SQL queries) connected to the DWH."""
    datasets = [
        {
            "name": "Environmental Daily Aggregated",
            "sql": """
                SELECT
                    istat_code,
                    source,
                    period_date,
                    (parameters->>'NO2')::float          AS no2,
                    (parameters->>'PM10')::float         AS pm10,
                    (parameters->>'PM2.5')::float        AS pm25,
                    (parameters->>'O3')::float           AS ozone,
                    (parameters->>'SO2')::float          AS so2,
                    (parameters->>'temperature')::float  AS temperature,
                    (parameters->>'relative_humidity')::float AS humidity,
                    (parameters->>'precipitation')::float     AS precipitation,
                    (parameters->>'wind_speed')::float        AS wind_speed,
                    station_count,
                    created_at
                FROM environmental_daily_aggregated
            """,
            "description": "IDW-aggregated daily environmental values per ISTAT comune. "
                           "One row per (istat_code, source, date). "
                           "Created by the Kafka IngestionConsumer.",
        },
        {
            "name": "Environmental Influenza Correlation",
            "sql": """
                SELECT
                    e.istat_code,
                    e.period_date,
                    (e.parameters->>'NO2')::float          AS no2,
                    (e.parameters->>'PM10')::float         AS pm10,
                    (e.parameters->>'PM2.5')::float        AS pm25,
                    (e.parameters->>'temperature')::float  AS temperature,
                    (e.parameters->>'relative_humidity')::float AS humidity,
                    (e.parameters->>'precipitation')::float     AS precipitation,
                    e.station_count
                FROM environmental_daily_aggregated e
                WHERE e.period_date >= NOW() - INTERVAL '3 years'
                ORDER BY e.istat_code, e.period_date
            """,
            "description": "Environmental data for the last 3 years — base for Influenza correlation analysis.",
        },
        {
            "name": "NO2 Daily by Comune",
            "sql": """
                SELECT
                    istat_code,
                    period_date,
                    (parameters->>'NO2')::float AS no2_ug_m3,
                    station_count
                FROM environmental_daily_aggregated
                WHERE parameters ? 'NO2'
                  AND (parameters->>'NO2')::float > 0
                ORDER BY period_date DESC
            """,
            "description": "Daily NO2 concentration per comune for time-series and map charts.",
        },
        {
            "name": "Temperature Daily by Comune",
            "sql": """
                SELECT
                    istat_code,
                    period_date,
                    (parameters->>'temperature')::float AS temperature_c,
                    (parameters->>'relative_humidity')::float AS humidity_pct,
                    (parameters->>'precipitation')::float AS precipitation_mm
                FROM environmental_daily_aggregated
                WHERE parameters ? 'temperature'
                ORDER BY period_date DESC
            """,
            "description": "Daily temperature, humidity and precipitation per comune.",
        },
        {
            "name": "Station Coverage Summary",
            "sql": """
                SELECT
                    source,
                    COUNT(DISTINCT istat_code)  AS comuni_count,
                    MIN(period_date)             AS earliest_date,
                    MAX(period_date)             AS latest_date,
                    COUNT(*)                     AS total_records,
                    AVG(station_count)           AS avg_stations_per_comune
                FROM environmental_daily_aggregated
                GROUP BY source
            """,
            "description": "Coverage summary: how many comuni and dates per data source.",
        },
    ]

    existing = client.get_existing_ids("/api/v1/dataset/", name_field="table_name")
    dataset_ids: Dict[str, int] = {}

    for ds in datasets:
        if ds["name"] in existing:
            dataset_ids[ds["name"]] = existing[ds["name"]]
            logger.info("Dataset already exists: %s", ds["name"])
            continue
        body = {
            "database": dwh_db_id,
            "table_name": ds["name"],
            "sql": ds["sql"],
            "description": ds.get("description", ""),
            "is_managed_externally": False,
        }
        result = client.post("/api/v1/dataset/", body)
        ds_id = result.get("id")
        if ds_id:
            dataset_ids[ds["name"]] = ds_id
            logger.info("Created dataset: %s (id=%d)", ds["name"], ds_id)
        else:
            logger.warning("Failed to create dataset: %s", ds["name"])

    return dataset_ids


def create_charts(client: SupersetClient, dataset_ids: Dict[str, int]) -> list:
    """Create starter charts for the HealthTrace dashboard."""
    charts = []

    # Chart 1: NO2 time series line chart
    no2_ds = dataset_ids.get("NO2 Daily by Comune")
    if no2_ds:
        body = {
            "slice_name": "NO₂ Daily Trend by Comune",
            "viz_type": "echarts_timeseries_line",
            "datasource_id": no2_ds,
            "datasource_type": "table",
            "params": json.dumps({
                "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "no2_ug_m3"}, "aggregate": "AVG", "label": "NO₂ μg/m³"}],
                "groupby": ["istat_code"],
                "x_axis": "period_date",
                "time_grain_sqla": "P1D",
                "show_legend": True,
                "x_axis_label": "Date",
                "y_axis_label": "NO₂ (μg/m³)",
                "rich_tooltip": True,
                "annotation_layers": [
                    {"value": 200, "name": "EU Limit 200 μg/m³", "style": "dashed", "color": "#FF0000"}
                ],
            }),
            "description": "Daily average NO₂ per comune with EU limit annotation.",
        }
        result = client.post("/api/v1/chart/", body)
        if result.get("id"):
            charts.append(result["id"])
            logger.info("Created chart: NO₂ Daily Trend (id=%d)", result["id"])

    # Chart 2: Temperature heatmap
    temp_ds = dataset_ids.get("Temperature Daily by Comune")
    if temp_ds:
        body = {
            "slice_name": "Temperature by Comune (Heatmap)",
            "viz_type": "heatmap_v2",
            "datasource_id": temp_ds,
            "datasource_type": "table",
            "params": json.dumps({
                "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "temperature_c"}, "aggregate": "AVG", "label": "Avg Temp °C"}],
                "groupby": ["istat_code"],
                "columns": ["period_date"],
            }),
            "description": "Heatmap of average daily temperature per comune over time.",
        }
        result = client.post("/api/v1/chart/", body)
        if result.get("id"):
            charts.append(result["id"])
            logger.info("Created chart: Temperature Heatmap (id=%d)", result["id"])

    # Chart 3: Station coverage big number
    cov_ds = dataset_ids.get("Station Coverage Summary")
    if cov_ds:
        body = {
            "slice_name": "Comuni Covered (DWH)",
            "viz_type": "big_number_total",
            "datasource_id": cov_ds,
            "datasource_type": "table",
            "params": json.dumps({
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "comuni_count"}, "aggregate": "SUM", "label": "Total Comuni"},
                "subheader": "ISTAT comuni with environmental data in DWH",
            }),
        }
        result = client.post("/api/v1/chart/", body)
        if result.get("id"):
            charts.append(result["id"])
            logger.info("Created chart: Comuni Coverage (id=%d)", result["id"])

    return charts


def create_dashboard(client: SupersetClient, chart_ids: list) -> Optional[int]:
    """Create the main HealthTrace Environmental Dashboard."""
    if not chart_ids:
        logger.warning("No charts to add to dashboard.")
        return None

    body = {
        "dashboard_title": "HealthTrace — Environmental Monitoring",
        "slug": "healthtrace-environmental",
        "published": True,
        "position_json": json.dumps({
            "DASHBOARD_VERSION_KEY": "v2",
            "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
            "GRID_ID": {
                "type": "GRID", "id": "GRID_ID",
                "children": [f"CHART-{cid}" for cid in chart_ids],
                "parents": ["ROOT_ID"],
            },
            **{
                f"CHART-{cid}": {
                    "type": "CHART",
                    "id": f"CHART-{cid}",
                    "meta": {"chartId": cid, "width": 6, "height": 50},
                    "parents": ["ROOT_ID", "GRID_ID"],
                    "children": [],
                }
                for cid in chart_ids
            },
        }),
    }
    result = client.post("/api/v1/dashboard/", body)
    dash_id = result.get("id")
    if dash_id:
        logger.info("Created dashboard: HealthTrace Environmental (id=%d)", dash_id)
        # Attach charts
        for cid in chart_ids:
            client.post(f"/api/v1/dashboard/{dash_id}/add_slices", {"slice_ids": [cid]})
    return dash_id


def main():
    parser = argparse.ArgumentParser(description="Bootstrap Superset for HealthTrace")
    parser.add_argument("--superset-url", default="http://localhost:8088")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin")
    args = parser.parse_args()

    try:
        client = SupersetClient(args.superset_url, args.username, args.password)
    except Exception as exc:
        logger.error("Cannot connect to Superset at %s: %s", args.superset_url, exc)
        sys.exit(1)

    db_ids = register_databases(client)
    dwh_id = db_ids.get("HealthTrace DWH")
    if not dwh_id:
        logger.error("HealthTrace DWH registration failed — cannot create datasets.")
        sys.exit(1)

    dataset_ids = register_datasets(client, dwh_id)
    chart_ids   = create_charts(client, dataset_ids)
    dash_id     = create_dashboard(client, chart_ids)

    print("\n=== Bootstrap complete ===")
    print(f"  Databases registered : {len(db_ids)}")
    print(f"  Datasets created     : {len(dataset_ids)}")
    print(f"  Charts created       : {len(chart_ids)}")
    print(f"  Dashboard id         : {dash_id}")
    print(f"\nOpen Superset: {args.superset_url}")
    print("  Username: admin / Password: admin (change in production!)")


if __name__ == "__main__":
    main()
