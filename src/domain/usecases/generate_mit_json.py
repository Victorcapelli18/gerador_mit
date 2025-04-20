import json
import os
from src.infrastructure.adapters.json_validator import validar_json
from src.domain.entities.mit_entity import Mit, PeriodoApuracao





class GeradorMitUseCase:
    def __init__(self, repository, pasta_saida: str, json_schema: dict):
        self.repository = repository
        self.pasta_saida = pasta_saida
        self.json_schema = json_schema
        self.erros_registrados = set()
        self.service = GeradorService()
        os.makedirs(pasta_saida, exist_ok=True)

    def executar(self):
        empresas = self.repository.obter_empresas()
        for nome in empresas:
            try:
                periodo_row, dados_row, df_debitos, df_susp = self.repository.carregar_dados(nome)

                mit = Mit(
                    periodo_apuracao=PeriodoApuracao(
                        mes_apuracao=periodo_row["mes_apuracao"],
                        ano_apuracao=periodo_row["ano_apuracao"]
                    ),
                    dados_iniciais=self.service.montar_dados_iniciais(dados_row),
                    debitos=self.service.montar_debitos(df_debitos),
                    lista_suspensoes=self.service.montar_suspensoes(df_susp)
                )