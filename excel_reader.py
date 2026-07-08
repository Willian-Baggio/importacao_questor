import pandas as pd

class ExcelReader:

    @staticmethod
    def read_first_column(file_path: str) -> list[str]:

        dataframe = pd.read_excel(file_path, header=None)

        first_column = (
            dataframe.iloc[:, 0]
            .fillna("")
            .astype(str)
            .tolist()
        )

        return first_column
    
    @staticmethod
    def clean_data(rows: list[str]) -> list[str]:

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