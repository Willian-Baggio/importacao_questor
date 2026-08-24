from dataclasses import dataclass

@dataclass
class ProductService:
    empresa: str
    produto: float
    servico: float
    receita: float
    imposto: float