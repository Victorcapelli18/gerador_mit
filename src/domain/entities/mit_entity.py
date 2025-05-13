from pydantic import BaseModel, Field, ConfigDict
from src.domain.entities.responsible_entity import ResponsavelApuracao
from typing import List, Optional, Dict, Any
import datetime


class PeriodoApuracao(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mes_apuracao: int = Field(..., alias="MesApuracao", ge=1, le=12)
    ano_apuracao: int = Field(..., alias="AnoApuracao", ge=2025)
    
    def periodo_formatado(self) -> str:
        """Retorna o período formatado como AAAAMM."""
        return f"{self.ano_apuracao}{str(self.mes_apuracao).zfill(2)}"
    
    def eh_valido(self) -> bool:
        """Verifica se o período de apuração é válido (não futuro)."""
        hoje = datetime.date.today()
        return (self.ano_apuracao < hoje.year or 
                (self.ano_apuracao == hoje.year and self.mes_apuracao <= hoje.month))


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
    
    def eh_postergado(self) -> bool:
        """Verifica se o débito é postergado."""
        return self.ano_postergado is not None and self.trim_postergado is not None


class Imposto(BaseModel):
    lista_debitos: List[Debito] =[]
    
    def valor_total(self) -> float:
        """Calcula o valor total dos débitos deste imposto."""
        return sum(debito.valor_debito or 0 for debito in self.lista_debitos)
    
    def adicionar_debito(self, debito: Debito) -> None:
        """Adiciona um débito à lista de débitos."""
        self.lista_debitos.append(debito)


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
    
    def valor_total(self) -> float:
        """Calcula o valor total de todos os impostos."""
        return (self.irpj.valor_total() + self.csll.valor_total() + 
                self.irrf.valor_total() + self.ipi.valor_total() +
                self.iof.valor_total() + self.pis_pasep.valor_total() +
                self.cofins.valor_total() + self.contribuicoes_diversas.valor_total() +
                self.cpss.valor_total())


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
    
    def valor_total_suspenso(self) -> float:
        """Calcula o valor total suspenso."""
        return sum(debito.valor_suspenso for debito in self.lista_debitos_suspensos)


class Mit(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    periodo_apuracao: PeriodoApuracao = Field(..., alias="PeriodoApuracao")
    dados_iniciais: DadosIniciais = Field(..., alias="DadosIniciais")
    debitos: Debitos = Field(..., alias="Debitos")
    lista_suspensoes: List[Suspensao] = Field(default_factory=list, alias="ListaSuspensoes")
    
    def eh_sem_movimento(self) -> bool:
        """Verifica se a declaração é sem movimento."""
        return self.dados_iniciais.sem_movimento
    
    def tem_debitos(self) -> bool:
        """Verifica se há débitos declarados."""
        return self.debitos.valor_total() > 0
    
    def tem_suspensoes(self) -> bool:
        """Verifica se há suspensões declaradas."""
        return len(self.lista_suspensoes) > 0
    
    def valor_total_debitos(self) -> float:
        """Retorna o valor total de débitos."""
        return self.debitos.valor_total()
    
    def valor_total_suspenso(self) -> float:
        """Retorna o valor total suspenso."""
        return sum(suspensao.valor_total_suspenso() for suspensao in self.lista_suspensoes)
    
    def gerar_nome_arquivo(self, nome_empresa: str) -> str:
        """Gera o nome do arquivo para esta declaração MIT."""
        periodo_str = self.periodo_apuracao.periodo_formatado()
        return f"{nome_empresa}--MIT--{periodo_str}.json"