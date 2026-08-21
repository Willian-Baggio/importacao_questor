import logging
from src.config.settings import REQUEST_TIMEOUT, MAX_RETRIES
import requests
import time

logger = logging.getLogger("automacao importacao para o questor")

class SittaxAPIError(Exception):
    pass

class SittaxClient:
    def __init__(self, base_url: str, email: str, password: str,
                 token: str, timeout: int = REQUEST_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.password = password
        self.token = token
        self.timeout = timeout
        
        
    def _create_url(self, endpoint: str):
        return f"{self.base_url}/{endpoint.lstrip("/")}"
    
    def _execute(self, method: str, endpoint: str, **kwargs) -> dict:
        url = self._create_url(endpoint)
        last_execption = None
        
        for attemp in range(1, MAX_RETRIES + 2):
            try:
                logger.info("Chamando %s %s (attemp %s)", method, url, attemp)
                response = self.session.request(
                    method,
                    url,
                    headers=self._headers(),
                    timeout=self.timeout,
                    **kwargs
                )
                
                if response.status_code == 401:
                    raise SittaxAPIError(
                        "Token JWT rejeitado, provavelmente expirou"
                    )
                
                response.raise_for_status()
                
                if not response.content:
                    return None
                
                try:
                    return response.json()
                except ValueError:
                    logger.info(f"Resposta de {url} não é um JSON válido - devolvendo None")
                    return None
            except requests.exceptions.RequestException as exc:
                last_execption = exc
                logger.warning("Falha na tentativa %s para %s: %s", attemp, url, exc)
                time.sleep(1)
                
        raise SittaxAPIError(f"Falha ao chamar {url} após {MAX_RETRIES + 1} tentativa(s): {last_execption}")