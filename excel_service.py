import pandas as pd
from constants import *

class ExcelService:

    @staticmethod
    def build_output_dataframe(
        dataframe: pd.DataFrame,
        report_date: str,
        ) -> pd.DataFrame:

        output = pd.DataFrame()

        output["CNPJ"] = dataframe["CNPJ"]
        output["Empresa"] = dataframe["Empresa"]

        output["Produtos"] = dataframe["Produtos"]
        output["Débito Produtos"] = "142"
        output["Crédito Produtos"] = "2655"
        output["Histórico Produtos"] = "3738"

        output["Serviços"] = dataframe["Serviços"]
        output["Débito Serviços"] = "142"
        output["Crédito Serviços"] = "2703"
        output["Histórico Serviços"] = "3737"

        output["Imposto DAS"] = dataframe["Imposto DAS"]
        output["Débito DAS"] = "2831"
        output["Crédito DAS"] = "1550"
        output["Histórico DAS"] = "177"

        output["Data"] = report_date

        return output


    @staticmethod
    def save(dataframe: pd.DataFrame, output_path: str):

        dataframe.to_excel(
            output_path,
            index=False
        )