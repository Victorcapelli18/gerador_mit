from src.domain.entities.excel_data_entity import PeriodoApuracao, DadosIniciais, Debito, Suspensao
from typing import List
from datetime import datetime

class ExcelMapper:

    def map_periodo_apuracao(self, dados: List[dict]) -> List[PeriodoApuracao]:
        return [
            PeriodoApuracao(
                empresa=linha["Empresa"],
                cnpj=linha["CNPJ"],
                mes_apuracao=int(linha["MesApuracao"]),
                ano_apuracao=int(linha["AnoApuracao"]),

            )
            for linha in dados
        ]
    
    def map_dados_iniciais(self, dados: List[dict]) -> List[DadosIniciais]:
        return [
            DadosIniciais(
                empresa=linha["Empresa"],
                sem_movimento=self._to_bool(linha["SemMovimento"]),
                qualificacao_pj=int(linha["QualificacaoPj"]),
                tributacao_lucro=int(linha["TributacaoLucro"]),
                variacoes_monetarias=int(linha["VariacoesMonetarias"]),
                regime_pis_cofins=int(linha["RegimePisCofins"]),
                cpf_responsavel=linha["CpfResponsavel"],
                uf_registro=linha["UfRegistro"],
                num_registro=linha["NumRegistro"],
                ddd=int(linha["Ddd"]),
                num_telefone=int(linha["NumTelefone"]),
                email_responsavel=linha["EmailResponsavel"],

            )
            for linha in dados
        ]
    
    def map_debitos(self, dados: List[dict]) -> List[Debito]:
        return [
            Debito(
                empresa=linha["Empresa"],
                imposto=linha["Imposto"],
                id_debito=linha.get("IdDebito") or None,
                codigo_debito=int(linha["CodigoDebito"]),
                valor_debito=self._to_float(linha.get("ValorDebito")),
                pa_debito=linha.get["PaDebito"] or None,
                codigo_municipio_ouro=linha.get["CodigoMunicipioOuro"] or None,
                cnpj_estabelecimento=linha.get["CnpjEstabelecimento"] or None,

            )
            for linha in dados
        ]
    
    def map_suspensoes(self, dados: List[dict]) -> List[Suspensao]:
        return [
            Suspensao(
                empresa=linha["Empresa"],
                tipo_suspensao=linha["TipoSuspensao"],
                motivo_suspensao=linha["MotivoSuspensao"],
                com_deposito=self._to_bool_or_none(linha.get("ComDeposito")),
                numero_processo=linha.get("NumeroProcesso") or None,
                processo_terceiro=linha.get("ProcessoTerceiro") or None,
                data_decisao=self._to_date_or_none(linha.get("DataDecisao")),
                vara_judiciaria=linha.get("VaraJudiciaria") or None,
                codigo_municipio_sj=linha.get("CodigoMunicipioSj") or None,
                id_debito_suspenso=linha.get("IdDebitoSuspenso") or None,
                valor_suspenso=self._to_float(linha.get("ValorSuspenso")),
            )
            for linha in dados
        ]

    # Métodos auxiliares

    def _to_bool(self, value) -> bool:
        return str(value).strip().lower() in ["1", "true", "sim"]

    def _to_bool_or_none(self, value) -> bool | None:
        if value in ["", None]:
            return None
        return self._to_bool(value)

    def _to_float(self, value) -> float | None:
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _to_date_or_none(self, value) -> datetime | None:
        if not value or str(value).strip() == "":
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None