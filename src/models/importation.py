from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class ProductService:
    cnpj: str
    empresa: str
    produto: float
    servico: float
    receita: float