from dataclasses import dataclass

@dataclass
class ReportRow:

    cnpj: str
    company: str
    products: str
    services: str
    gross_revenue: str
    das_percentage: str
    das_tax: str