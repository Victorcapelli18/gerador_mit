from pydantic import BaseModel, Field, ConfigDict
from src.domain.entities.responsible_entity import ResponsavelApuracao
from typing import List, Optional, Dict, Any
import datetime

class PeriodoApuracaoEntity(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mes_apuracao: int = Field(..., alias="MesApuracao", ge=1, le=12)
    ano_apuracao: int = Field(..., alias="AnoApuracao", ge=2025, le=2100)


    def periodo_formatado(self) -> str:
        """Retorna o período de apuração formatado como 'MM/YYYY'."""
        return f"{self.ano_apuracao}{str(self.mes_apuracao).zfill(2)}"
    
    def eh_valido(self) -> bool:
        """Verifica se o período de apuração é válido."""
        hoje = datetime.datetime.today()
        return (self.ano_apuracao > hoje.year or
                (self.ano_apuracao == hoje.year and self.mes_apuracao >= hoje.month))


class DadosIniciaisEntity(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sem_movimento: bool = Field(..., alias="SemMovimento")
    qualificacao_pj: int = Field(..., alias="QualificacaoPj", ge=1, le=12)
    tributacao_lucro: int = Field(..., alias="TributacaoLucro", ge=1, le=7)
    variacoes_monetarias: int = Field(..., alias="VariacoesMonetarias", ge=1, le=3)
    regime_pis_cofins: int = Field(..., alias="RegimePisCofins", ge=1, le=4)
    responsavel_apuracao: ResponsavelApuracao = Field(..., alias="ResponsavelApuracao")
    cnpj: Optional[str] = Field(None, alias="Cnpj")


class DebitoEntity(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id_debito: Optional[int] = Field(None, alias="IdDebito", ge=1)
    codigo_debito: str = Field(..., alias="CodigoDebito")
    valor_debito: Optional[float] = Field(None, alias="ValorDebito")
    id_evento_debito: Optional[int] = Field(None, alias="IdEventoDebito", ge=1, le=5)
    ano_postergado: Optional[int] = Field(None, alias="AnoPostergado")
    trim_postergado: Optional[int] = Field(None, alias="TrimPostergado", ge=1, le=4)
    ano_debito: Optional[int] = Field(None, alias="AnoDebito",)
    cnpj_scp: Optional[str] = Field(None, alias="CnpjSCP")

    def eh_postergado(self) -> bool:
        """Verifica se o débito é postergado."""
        return self.ano_postergado is not None and self.trim_postergado is not None


class ImpostoEntity(BaseModel):
    lista_debitos: list[DebitoEntity] = []

    def valor_total(self) -> float:
        """Calcula o valor total dos débitos deste imposto."""
        return sum(debito.valor_debito or 0 for debito in self.lista_debitos)
    
    def adicionar_debito(self, debito: DebitoEntity) -> None:
        """Adiciona um débito à lista de débitos do imposto."""
        self.lista_debitos.append(debito)


class DebitosEntity(BaseModel):
    balanco_lucro_real: bool
    irpj: ImpostoEntity = ImpostoEntity()
    csll: ImpostoEntity = ImpostoEntity()
    irrf: ImpostoEntity = ImpostoEntity()
    ipi: ImpostoEntity = ImpostoEntity()
    iof: ImpostoEntity = ImpostoEntity()
    pis_pasep: ImpostoEntity = ImpostoEntity()
    cofins: ImpostoEntity = ImpostoEntity()
    contribuicoes_diversas: ImpostoEntity = ImpostoEntity()
    cpss: ImpostoEntity = ImpostoEntity()

    def valor_total(self) -> float:
        """Calcula o valor total de todos os débitos."""
        return (self.irpj.valor_total() +
                self.csll.valor_total() +
                self.irrf.valor_total() +
                self.ipi.valor_total() +
                self.iof.valor_total() +
                self.pis_pasep.valor_total() +
                self.cofins.valor_total() +
                self.contribuicoes_diversas.valor_total() +
                self.cpss.valor_total())


class DebitoSuspensoEntity(BaseModel):
    id_debito_suspenso: int = Field(..., ge=1)
    valor_suspenso: float


class SuspensaoEntity(BaseModel):
    tipo_suspensao: int = Field(..., ge=1, le=2)
    motivo_suspensao: int = Field(..., enum=[1, 2, 4, 5, 8, 9, 10, 11, 12, 13])
    com_deposito: bool
    numero_processo: str
    processo_terceiro: Optional[bool] = None
    data_decisao: Optional[int]  = None
    vara_judiciaria: Optional[int] = Field(..., ge=1)
    codigo_municipio_sj: Optional[str] = None
    lista_debitos_suspensos: list[DebitoSuspensoEntity]
    def valor_total_suspenso(self) -> float:
        """Calcula o valor total dos débitos suspensos."""
        return sum(debito.valor_suspenso for debito in self.lista_debitos_suspensos)


class MitEntity(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    periodo_apuracao: PeriodoApuracaoEntity = Field(..., alias="PeriodoApuracao")
    dados_iniciais: DadosIniciaisEntity = Field(..., alias="DadosIniciais")
    debitos: DebitosEntity = Field(..., alias="Debitos")
    lista_suspensoes: list[SuspensaoEntity] = Field(default_factory=list, alias="ListaSuspensoes")

    def eh_sem_movimento(self) -> bool:
        """Verifica se o MIT é sem movimento."""
        return self.dados_iniciais.sem_movimento
    
    def tem_debitos(self) -> bool:
        """Verifica se o MIT possui débitos."""
        return self.debitos.valor_total() > 0
    
    def valor_total_debitos(self) -> float:
        """Calcula o valor total dos débitos do MIT."""
        return self.debitos.valor_total()
    
    def valor_total_suspenso(self) -> float:
        """Calcula o valor total dos débitos suspensos."""
        return sum(suspensao.valor_total_suspenso() for suspensao in self.lista_suspensoes)

    def gerar_nome_arquivo(self, cnpj: str) -> str:
        """Gera o nome do arquivo para o MIT."""
        periodo_str = self.periodo_apuracao.periodo_formatado()
        cnpj_raiz = cnpj[:8]
        return f"{cnpj_raiz}-MIT-{periodo_str}.json"