from pathlib import Path
from datetime import datetime

import pandas as pd


class JournalGenerator:

    IMPORTS_FOLDER_NAME = "Importações"

    @staticmethod
    def resolve_run_folder(report_date: str) -> Path:

        month_year = datetime.strptime(
            report_date,
            "%d/%m/%Y"
        ).strftime("%m-%Y")

        base_name = f"Importação-{month_year}"

        folder = Path(base_name)
        suffix = 2

        while folder.exists():
            folder = Path(f"{base_name}({suffix})")
            suffix += 1

        folder.mkdir(parents=True)
        (folder / JournalGenerator.IMPORTS_FOLDER_NAME).mkdir()

        return folder

    @staticmethod
    def generate(dataframe: pd.DataFrame, output_folder: Path):

        imports_folder = output_folder / JournalGenerator.IMPORTS_FOLDER_NAME

        for _, row in dataframe.iterrows():

            JournalGenerator.generate_company_file(row, imports_folder)

    @staticmethod
    def generate_company_file(row, imports_folder: Path):

        journal = JournalGenerator.build_journal_dataframe(row)

        if journal.empty:
            return

        company_name = JournalGenerator.sanitize_filename(
            row["Empresa"]
        )

        file_path = imports_folder / f"{company_name}.xlsx"

        journal.to_excel(
            file_path,
            index=False
        )

    @staticmethod
    def is_zero(value) -> bool:
        try:
            return float(str(value).replace(",", ".")) == 0
        except ValueError:
            return False

    @staticmethod
    def build_journal_dataframe(row):

        complement = JournalGenerator.get_complement(
            row["Data"]
        )

        candidates = [

            {
                "DATA": row["Data"],
                "DEBITO": row["Débito Produtos"],
                "CRÉDITO": row["Crédito Produtos"],
                "VALOR": row["Produtos"],
                "HISTÓRICO": row["Histórico Produtos"],
                "COMPLEMENTO": complement
            },

            {
                "DATA": row["Data"],
                "DEBITO": row["Débito Serviços"],
                "CRÉDITO": row["Crédito Serviços"],
                "VALOR": row["Serviços"],
                "HISTÓRICO": row["Histórico Serviços"],
                "COMPLEMENTO": complement
            },

            {
                "DATA": row["Data"],
                "DEBITO": row["Débito DAS"],
                "CRÉDITO": row["Crédito DAS"],
                "VALOR": row["Imposto DAS"],
                "HISTÓRICO": row["Histórico DAS"],
                "COMPLEMENTO": complement
            }

        ]

        records = [
            candidate for candidate in candidates
            if not JournalGenerator.is_zero(candidate["VALOR"])
        ]

        return pd.DataFrame(records)
    
    @staticmethod
    def get_complement(date_string):

        date = datetime.strptime(
            date_string,
            "%d/%m/%Y"
        )

        return date.strftime("%m/%Y")
    
    @staticmethod
    def sanitize_filename(filename):

        invalid = '<>:"/\\|?*'

        for char in invalid:
            filename = filename.replace(char, "")

        return filename.strip()