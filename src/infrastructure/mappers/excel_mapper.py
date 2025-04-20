from domain.entities.excel_data_entity import PeriodoApuracao, DadosIniciais, Debito, Suspensao
from typing import List
from datetime import datetime

class ExcelMapper:

    def map_periodo_apuracao(self, dados: List[dict]) -> List[PeriodoApuracao]:
        return [
            PeriodoApuracao(
                empresa=linha["empresa"],
                cnpj=linha["cnpj"],
                mes_apuracao=int(linha["mes_apuracao"]),
                ano_apuracao=int(linha["ano_apuracao"]),

            )
            for linha in dados
        ]
    
    def map_dados_iniciais(self, dados: List[dict]) -> List[DadosIniciais]:
        return [
            DadosIniciais(
                empresa=linha["empresa"],
                sem_movimento=self._to_bool(linha["sem_movimento"]),
                qualificacao_pj=int(linha["qualificacao_pj"]),
                tributacao_lucro=int(linha["tributacao_lucro"]),
                variacoes_monetarias=int(linha["variacoes_monetarias"]),
                regime_pis_cofins=int(linha["regime_pis_cofins"]),
                cpf_responsavel=linha["tributacao_lucro"],
                uf_registro=linha["uf_registro"],
                num_registro=linha["num_registro"],
                ddd=int(linha["ddd"]),
                num_telefone=int(linha["num_telefone"]),
                email_responsavel=linha["email_responsavel"],

            )
            for linha in dados
        ]
    
    def map_debitos(self, dados: List[dict]) -> List[Debito]:
        return [
            Debito(
                empresa=linha["empresa"],
                imposto=linha["imposto"],
                id_debito=linha.get("id_debito") or None,
                codigo_debito=int(linha["codigo_debito"]),
                valor_debito=self._to_float(linha.get("valor_debito")),
                pa_debito=linha.get["pa_debito"] or None,
                codigo_municipio_ouro=linha.get["codigo_municipio_ouro"] or None,
                cnpj_estabelecimento=linha.get["cnpj_estabelecimento"] or None,

            )
            for linha in dados
        ]
    
    def map_suspensoes(self, dados: List[dict]) -> List[Suspensao]:
        return [
            Suspensao(
                empresa=linha["empresa"],
                tipo_suspensao=linha["tipo_suspensao"],
                motivo_suspensao=linha["motivo_suspensao"],
                com_deposito=self._to_bool_or_none(linha.get("com_deposito")),
                numero_processo=linha.get("numero_processo") or None,
                processo_terceiro=linha.get("processo_terceiro") or None,
                data_decisao=self._to_date_or_none(linha.get("data_decisao")),
                vara_judiciaria=linha.get("vara_judiciaria") or None,
                codigo_municipio_sj=linha.get("codigo_municipio_sj") or None,
                id_debito_suspenso=linha.get("id_debito_suspenso") or None,
                valor_suspenso=self._to_float(linha.get("valor_suspenso")),
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