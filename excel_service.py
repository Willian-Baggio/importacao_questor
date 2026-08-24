import pandas as pd
from constants import (
    DAS_CREDIT,
    DAS_DEBIT,
    DAS_HISTORY,
    DEVOLUTION_CREDIT,
    DEVOLUTION_DEBIT,
    DEVOLUTION_HISTORY,
    PRODUCTS_CREDIT,
    PRODUCTS_DEBIT,
    PRODUCTS_HISTORY,
    SERVICES_CREDIT,
    SERVICES_DEBIT,
    SERVICES_HISTORY,
)

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
        output["Débito Produtos"] = PRODUCTS_DEBIT
        output["Crédito Produtos"] = PRODUCTS_CREDIT
        output["Histórico Produtos"] = PRODUCTS_HISTORY

        output["Serviços"] = dataframe["Serviços"]
        output["Débito Serviços"] = SERVICES_DEBIT
        output["Crédito Serviços"] = SERVICES_CREDIT
        output["Histórico Serviços"] = SERVICES_HISTORY

        output["Devolução"] = dataframe["Devolução"]
        output["Débito Devolução"] = DEVOLUTION_DEBIT
        output["Crédito Devolução"] = DEVOLUTION_CREDIT
        output["Histórico Devolução"] = DEVOLUTION_HISTORY

        output["Imposto DAS"] = dataframe["Imposto DAS"]
        output["Débito DAS"] = DAS_DEBIT
        output["Crédito DAS"] = DAS_CREDIT
        output["Histórico DAS"] = DAS_HISTORY

        output["Data"] = report_date

        return output


    @staticmethod
    def save(dataframe: pd.DataFrame, output_path: str):

        dataframe.to_excel(
            output_path,
            index=False
        )