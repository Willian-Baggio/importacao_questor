import logging
import os
from datetime import date, timedelta

from dotenv import load_dotenv

from src.config.settings import LOG_DIR
from src.services.import_service import ImportationService
from src.services.journal_builder import generate as generate_journals
from src.sittax.sittax_client import SittaxAPIError, SittaxClient

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

def previous_month_range(reference_date: date) -> tuple[int, int]:
    first_day_current_month = reference_date.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    return last_day_previous_month.month, last_day_previous_month.year

def run_for_competence(month: int, year: int) -> None:
    setup_logging()
    logging.info(f"Iniciando automação de importação Sittax -> Questor para {month:02d}/{year}")

    email = os.getenv("USER_EMAIL")
    password = os.getenv("USER_PASSWORD")

    if not email or not password:
        logger.error("USER_EMAIL e/ou USER_PASSWORD não configurados no .env")
        return

    try:
        sittax_client = SittaxClient(email, password)
        sittax_client.login()

        import_service = ImportationService(sittax_client)
        processed_companies, failed_companies = import_service.processed_competence(month, year)

        logger.info(f"{len(processed_companies)} empresa(s) processada(s) com sucesso")

        if failed_companies:
            logger.warning(f"{len(failed_companies)} empresa(s) com erro no processamento")

        generate_journals(processed_companies, failed_companies, month, year, date.today())

        for company in processed_companies:
            logger.info(f"Arquivo xlsx gerado para a empresa {company.empresa}")
    except SittaxAPIError as e:
        logger.error(f"Erro de comunicação com o Sittax: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Erro durante a execução: {e}", exc_info=True)

def main() -> None:
    month, year = previous_month_range(date.today())
    run_for_competence(month=month, year=year)

if __name__ == "__main__":
    main()