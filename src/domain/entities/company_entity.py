from pydantic import BaseModel, Field


class Company(BaseModel):
    codigo_sap: str
    cnpj_raiz: str
    cnpj: str = Field(..., min_length=14, max_length=14)
    qualificacao_pj: str
    tributacao_lucro: str
    variacoes_monetarias: str
    regime_pis_cofins: str