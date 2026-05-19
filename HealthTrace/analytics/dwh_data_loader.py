"""
DWH Data Loader
================
Joins the HealthTrace DWH (environmental_daily_aggregated) with the GESAN
malattie infettive database to produce ready-to-use DataFrames for the ML models.

Output schema (one row per istat_code per day):
  istat_code, period_date,
  # Air quality (ARPAC)
  NO2, PM10, PM2.5, O3, SO2,
  # Meteorology (MeteoHub)
  temperature, relative_humidity, precipitation, wind_speed, pressure,
  # Disease counts (GESAN — one column per target disease)
  influenza_cases, legionellosis_cases, hepatitis_a_cases,
  # Derived helpers
  rainy_days, extreme_precipitation, month, week_of_year, season

Usage:
    from analytics.dwh_data_loader import DwhDataLoader

    loader = DwhDataLoader()
    df = loader.load(
        disease="influenza",
        istat_codes=["063049", "063041"],
        date_from="2022-01-01",
        date_to="2023-12-31",
    )
    # df is ready to pass directly to any model in advanced_models.py
"""

import logging
from datetime import date
from typing import List, Optional

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

# ── GESAN disease name patterns ────────────────────────────────────────────────
# Maps our internal disease key → SQL ILIKE patterns for the GESAN
# `malattia` column (based on Italian disease names in the real DB).
DISEASE_PATTERNS = {
    "influenza":     ["%influenza%", "%flu%"],
    "legionellosis": ["%legion%", "%legionellosi%"],
    "hepatitis_a":   ["%epatite%a%", "%hepatitis%a%"],
}

# GESAN health DB connection (read-only)
GESAN_DB_URL = "postgresql://readonly:readonly@10.10.13.11:5432/gesan_malattieinfettive"

# ── Canonical parameter→column name map ───────────────────────────────────────
# Maps the parameter names stored in the JSONB `parameters` column
# to flat DataFrame column names expected by the ML models.
PARAM_COLUMN_MAP = {
    # Air quality
    "NO2":   "no2",
    "PM10":  "pm10",
    "PM2.5": "pm25",
    "O3":    "ozone",
    "SO2":   "so2",
    "CO":    "co",
    # Meteorology
    "Temperature":        "temperature",
    "temperature":        "temperature",
    "Relative_Humidity":  "relative_humidity",
    "relative_humidity":  "relative_humidity",
    "Precipitation_Amount": "precipitation",
    "precipitation":      "precipitation",
    "Wind_Speed":         "wind_speed",
    "wind_speed":         "wind_speed",
    "Pressure":           "pressure",
    "pressure":           "pressure",
}


class DwhDataLoader:
    """
    Loads and joins environmental DWH data with GESAN health data
    into a single flat DataFrame ready for ML model input.
    """

    def __init__(
        self,
        healthtrace_db_url: Optional[str] = None,
        gesan_db_url: Optional[str] = None,
    ):
        try:
            from app.core.config import settings
            ht_url = healthtrace_db_url or settings.DATABASE_URL
        except ImportError:
            ht_url = healthtrace_db_url or "postgresql://healthtrace:healthtrace_password@localhost:5433/healthtrace"

        self._ht_engine = create_engine(ht_url, pool_pre_ping=True)
        self._gesan_url = gesan_db_url or GESAN_DB_URL
        self._gesan_engine = None  # lazy — only connect when health data is needed

    # ── Public API ────────────────────────────────────────────────────────────

    def load(
        self,
        disease: str,
        istat_codes: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        min_env_stations: int = 1,
    ) -> pd.DataFrame:
        """
        Load a joined environmental + health DataFrame.

        Parameters
        ----------
        disease : "influenza" | "legionellosis" | "hepatitis_a"
        istat_codes : list of 6-digit ISTAT comune codes; None = all available
        date_from, date_to : ISO date strings "YYYY-MM-DD"
        min_env_stations : minimum station_count required in aggregated row

        Returns
        -------
        pd.DataFrame  — one row per (istat_code, period_date)
        """
        if disease not in DISEASE_PATTERNS:
            raise ValueError(f"Unknown disease '{disease}'. Choose from {list(DISEASE_PATTERNS)}")

        env_df = self._load_environmental(istat_codes, date_from, date_to, min_env_stations)
        if env_df.empty:
            logger.warning("No environmental data found for the requested filters.")
            return pd.DataFrame()

        health_df = self._load_health(disease, istat_codes, date_from, date_to)

        merged = self._join(env_df, health_df, disease)
        merged = self._add_derived_columns(merged)
        logger.info(
            "DWH load complete: disease=%s rows=%d comuni=%d",
            disease, len(merged), merged["istat_code"].nunique(),
        )
        return merged

    def load_all_diseases(
        self,
        istat_codes: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Load environmental data joined with all three target diseases simultaneously.
        Useful for comparative / multi-disease models.
        """
        env_df = self._load_environmental(istat_codes, date_from, date_to)
        if env_df.empty:
            return pd.DataFrame()

        health_dfs = {}
        for disease in DISEASE_PATTERNS:
            h = self._load_health(disease, istat_codes, date_from, date_to)
            if not h.empty:
                health_dfs[disease] = h

        result = env_df.copy()
        for disease, h_df in health_dfs.items():
            col = f"{disease}_cases"
            h_df = h_df.rename(columns={"case_count": col})
            result = result.merge(
                h_df[["istat_code", "period_date", col]],
                on=["istat_code", "period_date"],
                how="left",
            )
            result[col] = result[col].fillna(0).astype(int)

        return self._add_derived_columns(result)

    # ── Environmental data ────────────────────────────────────────────────────

    def _load_environmental(
        self,
        istat_codes: Optional[List[str]],
        date_from: Optional[str],
        date_to: Optional[str],
        min_stations: int = 1,
    ) -> pd.DataFrame:
        conditions = ["station_count >= :min_stations"]
        params: dict = {"min_stations": min_stations}

        if istat_codes:
            conditions.append("istat_code = ANY(:istat_codes)")
            params["istat_codes"] = istat_codes
        if date_from:
            conditions.append("period_date >= :date_from")
            params["date_from"] = date_from
        if date_to:
            conditions.append("period_date <= :date_to")
            params["date_to"] = date_to

        where = " AND ".join(conditions)
        sql = f"""
            SELECT istat_code, source, period_date, parameters, station_count
            FROM environmental_daily_aggregated
            WHERE {where}
            ORDER BY istat_code, period_date
        """
        try:
            with self._ht_engine.connect() as conn:
                rows = conn.execute(text(sql), params).fetchall()
        except Exception as exc:
            logger.error("Environmental DWH query failed: %s", exc)
            return pd.DataFrame()

        if not rows:
            return pd.DataFrame()

        # Flatten JSONB parameters into columns, pivot ARPAC + MeteoHub side by side
        records = []
        # Group by (istat_code, period_date) and merge both sources
        from collections import defaultdict
        grouped: dict = defaultdict(dict)
        for row in rows:
            key = (row.istat_code, str(row.period_date))
            params_dict = row.parameters or {}
            for raw_param, value in params_dict.items():
                col = PARAM_COLUMN_MAP.get(raw_param, raw_param.lower())
                grouped[key][col] = value
            grouped[key]["istat_code"] = row.istat_code
            grouped[key]["period_date"] = str(row.period_date)

        records = list(grouped.values())
        df = pd.DataFrame(records)
        df["period_date"] = pd.to_datetime(df["period_date"])
        return df

    # ── Health data (GESAN) ───────────────────────────────────────────────────

    def _load_health(
        self,
        disease: str,
        istat_codes: Optional[List[str]],
        date_from: Optional[str],
        date_to: Optional[str],
    ) -> pd.DataFrame:
        patterns = DISEASE_PATTERNS[disease]

        # Build ILIKE conditions
        like_clauses = " OR ".join(
            [f"LOWER(malattia) LIKE LOWER('{p}')" for p in patterns]
        )

        conditions = [f"({like_clauses})"]
        params: dict = {}

        if istat_codes:
            conditions.append("comune_inizio_sintomi_codice_istat = ANY(:istat_codes)")
            params["istat_codes"] = istat_codes
        if date_from:
            conditions.append("data_inizio_sintomi >= :date_from")
            params["date_from"] = date_from
        if date_to:
            conditions.append("data_inizio_sintomi <= :date_to")
            params["date_to"] = date_to

        where = " AND ".join(conditions)
        sql = f"""
            SELECT
                comune_inizio_sintomi_codice_istat  AS istat_code,
                DATE(data_inizio_sintomi)           AS period_date,
                COUNT(*)                            AS case_count
            FROM malattie_infettive
            WHERE {where}
              AND comune_inizio_sintomi_codice_istat IS NOT NULL
              AND data_inizio_sintomi IS NOT NULL
            GROUP BY 1, 2
            ORDER BY 1, 2
        """
        try:
            if self._gesan_engine is None:
                self._gesan_engine = create_engine(self._gesan_url, pool_pre_ping=True)
            with self._gesan_engine.connect() as conn:
                df = pd.read_sql(text(sql), conn, params=params)
            df["period_date"] = pd.to_datetime(df["period_date"])
            return df
        except Exception as exc:
            logger.warning("GESAN health DB query failed (%s) — using zeros: %s", disease, exc)
            return pd.DataFrame(columns=["istat_code", "period_date", "case_count"])

    # ── Join ──────────────────────────────────────────────────────────────────

    def _join(
        self,
        env_df: pd.DataFrame,
        health_df: pd.DataFrame,
        disease: str,
    ) -> pd.DataFrame:
        """Left-join environmental onto health; fill missing case counts with 0."""
        case_col = "case_count"
        merged = env_df.merge(
            health_df[["istat_code", "period_date", case_col]],
            on=["istat_code", "period_date"],
            how="left",
        )
        merged[case_col] = merged[case_col].fillna(0).astype(int)
        # Rename to model-expected column
        merged = merged.rename(columns={case_col: "case_count"})
        return merged

    # ── Derived columns ───────────────────────────────────────────────────────

    @staticmethod
    def _add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Add calendar and weather-derived columns used by several models."""
        if df.empty:
            return df

        df = df.copy()
        df["period_date"] = pd.to_datetime(df["period_date"])
        df["month"]        = df["period_date"].dt.month
        df["week_of_year"] = df["period_date"].dt.isocalendar().week.astype(int)
        df["day_of_year"]  = df["period_date"].dt.dayofyear

        def _season(m: int) -> str:
            if m in (12, 1, 2):  return "winter"
            if m in (3, 4, 5):   return "spring"
            if m in (6, 7, 8):   return "summer"
            return "autumn"

        df["season"] = df["month"].map(_season)

        # Precipitation-based helpers (used by Hepatitis A and Influenza models)
        if "precipitation" in df.columns:
            df["rainy_days"] = (df["precipitation"] > 1.0).astype(int)
            df["extreme_precipitation"] = (df["precipitation"] > 20.0).astype(int)
        else:
            df["rainy_days"] = 0
            df["extreme_precipitation"] = 0

        # Temperature-based helpers
        if "temperature" in df.columns:
            df["temperature_avg"] = df["temperature"]   # alias expected by older model code
            df["heat_wave"] = (df["temperature"] > 35.0).astype(int)
        
        # Sort
        df = df.sort_values(["istat_code", "period_date"]).reset_index(drop=True)
        return df

    # ── Convenience: available date range ────────────────────────────────────

    def available_range(self, istat_code: Optional[str] = None) -> dict:
        """Return earliest and latest dates available in the DWH."""
        params: dict = {}
        where = "WHERE istat_code = :ic" if istat_code else ""
        if istat_code:
            params["ic"] = istat_code
        sql = f"SELECT MIN(period_date), MAX(period_date), COUNT(DISTINCT istat_code) FROM environmental_daily_aggregated {where}"
        try:
            with self._ht_engine.connect() as conn:
                row = conn.execute(text(sql), params).fetchone()
            return {
                "date_from":    str(row[0]) if row[0] else None,
                "date_to":      str(row[1]) if row[1] else None,
                "comuni_count": row[2],
            }
        except Exception as exc:
            logger.error("available_range query failed: %s", exc)
            return {}
