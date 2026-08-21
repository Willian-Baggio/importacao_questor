from pathlib import Path

SITTAX_BASE_URL = "https://api.sittax.com.br"
SITTAX_LOGIN_URL = "https://app.sittax.com.br/auth/login"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 2

PROJECT_ROOT_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT_DIR / "log"