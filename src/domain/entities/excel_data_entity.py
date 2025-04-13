from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class PeriodoApuracao:
    empresa: str
    cnpj: str
    mes_apuracao: int
    ano_apuracao: int

@dataclass
class DadosIniciais:
    empresa: str
    sem_movimento: bool
    qualificacao_pj: int
    tributacao_lucro: int
    variacoes_monetarias: int
    regime_pis_cofins: int
    cpf_responsavel: str
    uf_registro: str
    num_registro: str
    ddd: int
    num_telefone: int
    email_responsavel: str

@dataclass
class Debito:
    empresa: str
    imposto: str
    id_debito: Optional[str]
    codigo_debito: int
    valor_debito: Optional[float]
    pa_debito: Optional[str]
    codigo_municipio_ouro: Optional[str]
    cnpj_estabelecimento: Optional[str]

@dataclass
class Suspensao:
    empresa: str
    tipo_suspensao: str
    motivo_suspensao: str
    com_deposito: Optional[bool]
    numero_processo: Optional[str]
    processo_terceiro: Optional[str]
    data_decisao: Optional[datetime]
    vara_judiciaria: Optional[str]
    codigo_municipio_sj: Optional[str]
    id_debito_suspenso: Optional[str]
    valor_suspenso: Optional[float]