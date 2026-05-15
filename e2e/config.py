import os

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:5173").rstrip("/")
API_URL = os.getenv("E2E_API_URL", "http://localhost:8000").rstrip("/")
ADMIN_EMAIL = os.getenv("E2E_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("E2E_ADMIN_PASSWORD", "changeme123")
HEADLESS = os.getenv("E2E_HEADLESS", "true").lower() in ("1", "true", "yes")
IMPLICIT_WAIT_SEC = float(os.getenv("E2E_IMPLICIT_WAIT", "0"))
EXPLICIT_WAIT_SEC = float(os.getenv("E2E_EXPLICIT_WAIT", "15"))
