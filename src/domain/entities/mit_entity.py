from pydantic import BaseModel, Field
from src.domain.entities.responsible_entity import ResponsavelApuracao
from typing import List, Optional


class PeriodoApuracao(BaseModel):
    mes_apuracao: int = Field(..., ge=1, le=12)
    ano_apuracao: int = Field(..., ge=2025)


class DadosIniciais(BaseModel):
    sem_movimento: bool = Field(...)
    qualificacao_pj: int = Field(..., ge=1, le=12)
    tributacao_lucro: int =  Field(..., ge=1, le=7)
    variacoes_monterias: int = Field(..., ge=1, le=3)
    regime_pis_cofins: int = Field(..., ge=1, le=4)
    responsavel_apuracao: ResponsavelApuracao


class Debito(BaseModel):
    id_debito: int = Field(..., ge=1)
    codigo_debito: str
    valor_debito: float
    id_evento_debito: Optional[int] = Field(None, ge=1, le=5)
    ano_postergado: Optional[int] = None
    trim_postergado: Optional[int] = Field(None, ge=1, le=4)
    ano_debito: Optional[int] = None
    cnpj_scp: Optional[str] = None


class Imposto(BaseModel):
    lista_debitos: List[Debito] =[]


class Debitos(BaseModel):
    balanco_lucro_real: bool
    irpj: Imposto = Imposto()
    csll: Imposto = Imposto()
    irrf: Imposto = Imposto()
    ipi: Imposto = Imposto()
    iof: Imposto = Imposto()
    pis_pasep: Imposto = Imposto()
    cofins: Imposto = Imposto()
    contribuicoes_diversas: Imposto = Imposto()
    cpss: Imposto = Imposto()


class DebtioSuspeno(BaseModel):
    id_debito_suspeno: int = Field(..., ge=1)
    valor_suspenso: float

class Suspensao(BaseModel):
    tipo_suspensao: int = Field(..., ge=1, le=2)
    motivo_suspensao: int = Field(..., enum=[1, 2, 4, 5, 8, 9, 10, 11, 12, 13])
    com_deposito: bool
    numero_processo: str
    processo_terceiro: Optional[bool] = None
    data_decisao: Optional[int] = None
    vara_jucidiaria: Optional[int] = Field(..., ge=1)
    codigo_municipio_sj: Optional[str] = None
    lista_debitos_suspensos: List[DebtioSuspeno]
    

class Mit(BaseModel):
    periodo_apuracao: PeriodoApuracao
    dados_iniciais: DadosIniciais
    debitos: Debitos
    lista_suspensoes: List[Suspensao] = []