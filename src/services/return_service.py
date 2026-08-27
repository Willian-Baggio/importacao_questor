import logging

from src.sittax.sittax_client import SittaxClient

class ReturnService:
     def __init__(self, sittax_client: SittaxClient):
        self.client = sittax_client
        self.logger = logging.getLogger("automacao importacao para o questor")
        
    