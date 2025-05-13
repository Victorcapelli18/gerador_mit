from pydantic import BaseModel, Field, ConfigDict
from src.domain.entities.responsible_entity import ResponsavelApuracao
from typing import List, Optional


class PeriodoApuracao(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mes_apuracao: int = Field(..., alias="MesApuracao", ge=1, le=12)
    ano_apuracao: int = Field(..., alias="AnoApuracao", ge=2025)


class DadosIniciais(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sem_movimento: bool = Field(..., alias="SemMovimento")
    qualificacao_pj: int = Field(..., alias="QualificacaoPj", ge=1, le=12)
    tributacao_lucro: int =  Field(..., alias="TributacaoLucro", ge=1, le=7)
    variacoes_monetarias: int = Field(..., alias="VariacoesMonetarias", ge=1, le=3)
    regime_pis_cofins: int = Field(..., alias="RegimePisCofins", ge=1, le=4)
    responsavel_apuracao: ResponsavelApuracao = Field(..., alias="ResponsavelApuracao")


class Debito(BaseModel):
    id_debito: Optional[int] = Field(None, ge=1)
    codigo_debito: str
    valor_debito: Optional[float] = None
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


class DebitoSuspeno(BaseModel):
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
    lista_debitos_suspensos: List[DebitoSuspeno]
    

class Mit(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    periodo_apuracao: PeriodoApuracao = Field(..., alias="PeriodoApuracao")
    dados_iniciais: DadosIniciais = Field(..., alias="DadosIniciais")
    debitos: Debitos = Field(..., alias="Debitos")
    lista_suspensoes: List[Suspensao] = Field(default_factory=list, alias="ListaSuspensoes")