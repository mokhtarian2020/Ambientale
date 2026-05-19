"""
Aggregated Environmental Data Endpoints
========================================
Exposes the IDW-aggregated daily environmental values per comune that are
written by the Kafka IngestionConsumer.

These are the "clean" environmental values the analytics models consume:
  one row per (istat_code, source, date), already weighted by station proximity.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.environmental import EnvironmentalDailyAggregated

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
def get_aggregated_data(
    istat_code: Optional[str] = Query(None, description="Filter by 6-digit ISTAT comune code"),
    source: Optional[str] = Query(None, description="ARPAC or METEOHUB"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Return IDW-aggregated daily environmental values per comune.
    Results are ordered by period_date descending.
    """
    q = db.query(EnvironmentalDailyAggregated)
    if istat_code:
        q = q.filter(EnvironmentalDailyAggregated.istat_code == istat_code)
    if source:
        q = q.filter(EnvironmentalDailyAggregated.source == source.upper())
    if date_from:
        q = q.filter(EnvironmentalDailyAggregated.period_date >= date_from)
    if date_to:
        q = q.filter(EnvironmentalDailyAggregated.period_date <= date_to)

    rows = q.order_by(EnvironmentalDailyAggregated.period_date.desc()).limit(limit).all()

    return [
        {
            "id": r.id,
            "istat_code": r.istat_code,
            "source": r.source,
            "period_date": r.period_date.isoformat(),
            "parameters": r.parameters,
            "station_count": r.station_count,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/summary", response_model=Dict[str, Any])
def get_aggregation_summary(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Summary statistics: how many comuni and date ranges are covered per source.
    """
    results = (
        db.query(
            EnvironmentalDailyAggregated.source,
            func.count(EnvironmentalDailyAggregated.id).label("total_records"),
            func.count(func.distinct(EnvironmentalDailyAggregated.istat_code)).label("comuni_count"),
            func.min(EnvironmentalDailyAggregated.period_date).label("earliest_date"),
            func.max(EnvironmentalDailyAggregated.period_date).label("latest_date"),
        )
        .group_by(EnvironmentalDailyAggregated.source)
        .all()
    )

    return {
        "sources": [
            {
                "source": r.source,
                "total_records": r.total_records,
                "comuni_count": r.comuni_count,
                "earliest_date": r.earliest_date.isoformat() if r.earliest_date else None,
                "latest_date": r.latest_date.isoformat() if r.latest_date else None,
            }
            for r in results
        ]
    }


@router.get("/{istat_code}/{period_date}", response_model=Dict[str, Any])
def get_aggregated_by_comune_date(
    istat_code: str,
    period_date: date,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Retrieve all available sources for a single comune on a specific date.
    Returns a merged parameter dict with source attribution.
    """
    rows = (
        db.query(EnvironmentalDailyAggregated)
        .filter(
            EnvironmentalDailyAggregated.istat_code == istat_code,
            EnvironmentalDailyAggregated.period_date == period_date,
        )
        .all()
    )

    if not rows:
        return {"istat_code": istat_code, "period_date": period_date.isoformat(), "data": {}}

    merged: Dict[str, Any] = {}
    for r in rows:
        for param, value in (r.parameters or {}).items():
            if param not in merged:
                merged[param] = {"value": value, "source": r.source, "station_count": r.station_count}

    return {
        "istat_code": istat_code,
        "period_date": period_date.isoformat(),
        "data": merged,
    }
