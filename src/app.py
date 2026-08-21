import calendar
import logging
import os
from datetime import date, timedelta

from dotenv import load_dotenv
from src.config.settings import LOG_DIR

load_dotenv()

logger = logging.getLogger("automacao importacao para o questor")

def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_DIR / "automacao importacao para o questor.log",
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        encoding="utf-8",
    )
    
def previous_month_range(reference_date: date) -> tuple[date, date]:
    pass

def run_for_competence(month: int, year: int):
    setup_logging()
    logging.info(f"Iniciando automação de importação Sittax -> Questor para {month:02d}/{year}")
    
    email = os.getenv("USER_EMAIL")
    password = os.getenv("USER_PASSWORD")
    if not email or not password:
        logger.error("USER_EMAIL e/ou USER_LOGIN não configurados no .env")
        return
    
    try:
        pass
    except Exception:
        pass
    
def main() -> None:
    month_and_year = previous_month_range(date.today())
    run_for_competence(month=month_and_year.month, year=month_and_year.year)
    
if __name__ == "__main__":
    main()