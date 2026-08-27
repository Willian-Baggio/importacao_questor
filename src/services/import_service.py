import logging

from src.models.importation import ProductService
from src.sittax.sittax_client import SittaxClient


class ImportationService:

    def __init__(self, sittax_client: SittaxClient):
        self.client = sittax_client
        self.logger = logging.getLogger("automacao importacao para o questor")
        self.processed_company: list[ProductService] = []
        self.failed_company: list[dict] = []

    def processed_competence(self, month: int, year: int) -> tuple[list[ProductService], list[dict]]:
        self.processed_company = []
        self.failed_company = []
        competence = f"{month:02d}/{year}"

        self.logger.info(f"Processando competência {competence}")

        self.client.set_period_cookie(month, year)

        company_data = self.client.get_company_data()

        for data in company_data:
            nome_empresa = data.get("empresa") or "Empresa desconhecida"
            try:
                company = self._create_product_service(data)
                self.processed_company.append(company)
                self.logger.info(f"Empresa processada: {company.empresa}")
            except Exception as e:
                self.logger.error(f"Erro ao processar empresa {nome_empresa}: {e}")
                self.failed_company.append({"Empresa": nome_empresa, "Erro": str(e)})

        return self.processed_company, self.failed_company

    def _create_product_service(self, data: dict) -> ProductService:
        empresa = data.get("empresa")

        if not empresa:
            raise ValueError("Empresa sem nome retornada pelo Sittax")

        cnpj = data.get("cnpj")
        devolucao = self.client.get_return(cnpj) if cnpj else 0.0

        return ProductService(
            empresa=empresa,
            produto=float(data.get("produto") or 0),
            servico=float(data.get("servico") or 0),
            receita=float(data.get("receita") or 0),
            imposto=float(data.get("imposto") or 0),
            devolucao=devolucao,
        )

    def get_processed_company(self) -> list[ProductService]:
        return self.processed_company

    def get_failed_company(self) -> list[dict]:
        return self.failed_company
