"""
Superset configuration for HealthTrace.
Mounted into the container at /app/pythonpath/superset_config.py.
"""

import os

SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "healthtrace-superset-secret-change-in-prod")

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://superset:superset_password@superset-db:5432/superset",
)

# Allow embedding dashboards in iframes (for HealthTrace frontend)
SESSION_COOKIE_SAMESITE = None
TALISMAN_ENABLED = False
WTF_CSRF_ENABLED = False          # disable for API access; re-enable in production
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "resources": ["*"],
    "origins": ["http://localhost:3200", "http://localhost:8001"],
}

# Row limit for large environmental datasets
ROW_LIMIT = 50_000
VIZ_ROW_LIMIT = 50_000

# Caching (uses Redis if available)
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/1")
try:
    from cachelib.redis import RedisCache
    CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": 300,
        "CACHE_KEY_PREFIX": "superset_",
        "CACHE_REDIS_URL": REDIS_URL,
    }
    DATA_CACHE_CONFIG = CACHE_CONFIG
except ImportError:
    pass

FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,   # allow Jinja in SQL queries
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
}
