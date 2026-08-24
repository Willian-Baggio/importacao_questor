import logging
from datetime import date
from pathlib import Path

import pandas as pd

from constants import (
    DAS_CREDIT,
    DAS_DEBIT,
    DAS_HISTORY,
    PRODUCTS_CREDIT,
    PRODUCTS_DEBIT,
    PRODUCTS_HISTORY,
    SERVICES_CREDIT,
    SERVICES_DEBIT,
    SERVICES_HISTORY,
)
from src.config.settings import OUTPUT_ERROR_DIR, OUTPUT_SUCCESS_DIR
from src.models.importation import ProductService

logger = logging.getLogger("automacao importacao para o questor")

IMPORTS_FOLDER_NAME = "Importações"


def _resolve_run_folder(root: Path, month: int, year: int) -> Path:
    base_name = f"Importação-{month:02d}-{year}"
    folder = root / base_name
    suffix = 2

    while folder.exists():
        folder = root / f"{base_name}({suffix})"
        suffix += 1

    folder.mkdir(parents=True)
    return folder


def _sanitize_filename(filename: str) -> str:
    invalid = '<>:"/\\|?*'

    for char in invalid:
        filename = filename.replace(char, "")

    return filename.strip()


def _is_zero(value) -> bool:
    try:
        return float(value) == 0
    except (TypeError, ValueError):
        return False


def _build_journal_dataframe(company: ProductService, run_date: date, complement: str) -> pd.DataFrame:
    data_lancamento = run_date.strftime("%d/%m/%Y")

    candidates = [
        {
            "DATA": data_lancamento,
            "DEBITO": PRODUCTS_DEBIT,
            "CRÉDITO": PRODUCTS_CREDIT,
            "VALOR": company.produto,
            "HISTÓRICO": PRODUCTS_HISTORY,
            "COMPLEMENTO": complement,
        },
        {
            "DATA": data_lancamento,
            "DEBITO": SERVICES_DEBIT,
            "CRÉDITO": SERVICES_CREDIT,
            "VALOR": company.servico,
            "HISTÓRICO": SERVICES_HISTORY,
            "COMPLEMENTO": complement,
        },
        {
            "DATA": data_lancamento,
            "DEBITO": DAS_DEBIT,
            "CRÉDITO": DAS_CREDIT,
            "VALOR": company.imposto,
            "HISTÓRICO": DAS_HISTORY,
            "COMPLEMENTO": complement,
        },
    ]

    records = [candidate for candidate in candidates if not _is_zero(candidate["VALOR"])]

    return pd.DataFrame(records)


def generate(
    processed_companies: list[ProductService],
    failed_companies: list[dict],
    month: int,
    year: int,
    run_date: date,
) -> Path | None:
    complement = f"{month:02d}/{year}"
    success_folder = None

    if processed_companies:
        success_folder = _resolve_run_folder(OUTPUT_SUCCESS_DIR, month, year)
        imports_folder = success_folder / IMPORTS_FOLDER_NAME
        imports_folder.mkdir()

        summary_rows = []

        for company in processed_companies:
            journal = _build_journal_dataframe(company, run_date, complement)

            if journal.empty:
                logger.info(f"Empresa {company.empresa} sem valores no período - nenhum arquivo gerado")
                continue

            file_name = f"{_sanitize_filename(company.empresa)} - {year}-{month:02d}.xlsx"
            journal.to_excel(imports_folder / file_name, index=False)

            summary_rows.append(
                {
                    "Empresa": company.empresa,
                    "Produtos": company.produto,
                    "Serviços": company.servico,
                    "Receita": company.receita,
                    "Imposto DAS": company.imposto,
                }
            )

        if summary_rows:
            pd.DataFrame(summary_rows).to_excel(success_folder / "Relatório.xlsx", index=False)

    if failed_companies:
        error_folder = _resolve_run_folder(OUTPUT_ERROR_DIR, month, year)
        pd.DataFrame(failed_companies).to_excel(error_folder / "Relatório_Erros.xlsx", index=False)
        logger.warning(f"{len(failed_companies)} empresa(s) com erro - detalhes em {error_folder}")

    return success_folder
