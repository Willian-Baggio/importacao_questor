import pandas as pd
from models import ReportRow

class ReportParser:

    @staticmethod
    def clean(rows: list[str]) -> list[str]:
        cleaned_rows = []

        for row in rows:

            value = row.strip()

            if not value:
                continue

            if value.startswith("Faturamento"):
                continue

            if value == "Ações":
                continue

            cleaned_rows.append(value)

        return cleaned_rows

    @staticmethod
    def clean_currency(value: str) -> str:
        value = value.replace("R$", "").replace("\xa0", "").strip()
        return value.replace(".", "")

    @staticmethod
    def parse(rows: list[str]) -> pd.DataFrame:

        records = []

        for i in range(0, len(rows), 7):

            block = rows[i:i + 7]

            if len(block) != 7:
                continue

            records.append({
                "CNPJ": block[0],
                "Empresa": block[1],
                "Produtos": ReportParser.clean_currency(block[2]),
                "Serviços": ReportParser.clean_currency(block[3]),
                "Imposto DAS": ReportParser.clean_currency(block[6])
            })

        return pd.DataFrame(records)