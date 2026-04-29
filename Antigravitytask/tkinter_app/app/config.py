"""
Application configuration settings.

Centralizes all configuration constants including database credentials,
application defaults, and fine calculation parameters.
"""


# ── Database Configuration ──────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "ghazanfar",
    "password": "zylo1234",
    "database": "library_db",
}

# ── Application Constants ───────────────────────────────────────────────
APP_TITLE = "Library Management System"
APP_WIDTH = 1200
APP_HEIGHT = 700

# ── Lending Defaults ────────────────────────────────────────────────────
LENDING_PERIOD_DAYS = 14
FINE_PER_DAY = 1.00  # Dollars per overdue day

# ── Default Admin Account ───────────────────────────────────────────────
DEFAULT_ADMIN_USERNAME = "ghazanfar"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_ROLE = "admin"
