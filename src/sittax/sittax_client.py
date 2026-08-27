import logging
import time

import requests

from src.config.endpoints import AUTH_LOGIN_URL, COMPANY_AUDIT, LIST_TRANSMITED_APURATION
from src.config.settings import LISTING_PAGE_SIZE, MAX_RETRIES, REQUEST_TIMEOUT

logger = logging.getLogger("automacao importacao para o questor")


class SittaxAPIError(Exception):
    pass


class SittaxClient:
    def __init__(self, email: str, password: str, timeout: int = REQUEST_TIMEOUT):
        self.email = email
        self.password = password
        self.timeout = timeout
        self.session = requests.Session()
        self.token = None

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    def _execute(self, method: str, url: str, **kwargs) -> dict | None:
        last_exception = None

        for attempt in range(1, MAX_RETRIES + 2):
            try:
                logger.info("Chamando %s %s (tentativa %s)", method, url, attempt)
                response = self.session.request(
                    method,
                    url,
                    headers=self._headers(),
                    timeout=self.timeout,
                    **kwargs,
                )

                if response.status_code == 401:
                    raise SittaxAPIError("Token JWT rejeitado, provavelmente expirou")

                response.raise_for_status()

                if not response.content:
                    return None

                try:
                    return response.json()
                except ValueError:
                    logger.info("Resposta de %s não é um JSON válido - devolvendo None", url)
                    return None
            except requests.exceptions.RequestException as exc:
                last_exception = exc
                logger.warning("Falha na tentativa %s para %s: %s", attempt, url, exc)
                time.sleep(1)

        raise SittaxAPIError(f"Falha ao chamar {url} após {MAX_RETRIES + 1} tentativa(s): {last_exception}")

    def login(self) -> None:
        payload = self._execute(
            "POST",
            AUTH_LOGIN_URL,
            json={"usuario": self.email, "senha": self.password},
        )

        token = payload.get("token") if payload else None

        if not token:
            raise SittaxAPIError("Login no Sittax não retornou um token válido")

        self.token = token
        logger.info("Login no Sittax realizado com sucesso")

    def get_company_data(self, page_size: int = LISTING_PAGE_SIZE) -> list[dict]:
        if not self.token:
            raise SittaxAPIError("É necessário fazer login antes de listar as empresas")

        companies = []
        page_number = 1

        while True:
            payload = self._execute(
                "POST",
                LIST_TRANSMITED_APURATION,
                json={"paginacao": {"pageNumber": page_number, "pageSize": page_size}},
            )

            tuples = (payload or {}).get("data", {}).get("dataSet", {}).get("tuples", [])

            companies.extend(tuples)

            if len(tuples) < page_size:
                break

            page_number += 1

        logger.info("Total de empresas retornadas pelo Sittax: %s", len(companies))
        return companies

    def set_period_cookie(self, month: int, year: int) -> None:
        value = f"{year:04d}-{month:02d}-01T03:00:00.000Z"
        self.session.cookies.set("DataInicialSelecionada", value, domain=".sittax.com.br", path="/")
        logger.info("Cookie DataInicialSelecionada definido como %s", value)

    def get_return(self, cnpj: str) -> float:
        if not self.token:
            raise SittaxAPIError("É necessário fazer login antes de consultar devoluções")

        payload = self._execute(
            "POST",
            COMPANY_AUDIT,
            json={"empresasCNPJ": [cnpj], "transmitido": True},
        )

        total = (payload or {}).get("data", {}).get("total")

        return float(total) if total else 0.0
            
            