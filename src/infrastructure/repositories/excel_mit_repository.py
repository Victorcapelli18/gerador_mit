import pandas as pd
from src.infrastructure.adapters.excel_adpter import ExcelAdapter
from src.infrastructure.mappers.excel_mapper import ExcelMapper


class ExcelMitRepository:
    def __init__(self, caminho_arquivo: str):
        self.adapter = ExcelAdapter()
        self.mapper = ExcelMapper()
        self.dados = self.adapter.carregar_planilha_excel(caminho_arquivo)


    def obter_empresas(self) -> list[str]:
        return list({linha["Empresa"] for linha in self.dados["DadosIniciais"]})
    

    def carregar_dados(self, empresa: str):
        filtro = lambda d: d["Empresa"] == empresa

        dados_periodo = list(filter(filtro, self.dados["PeriodoApuracao"]))
        dados_iniciais = list(filter(filtro, self.dados["DadosIniciais"]))
        dados_debitos = list(filter(filtro, self.dados["Debitos"]))
        dados_suspensoes = list(filter(filtro, self.dados["ListaSuspensoes"]))

        return(
            self.mapper.map_periodo_apuracao(dados_periodo)[0],
            self.mapper.map_dados_iniciais(dados_iniciais)[0].__dict__,
            pd.DataFrame(dados_debitos),
            pd.DataFrame(dados_suspensoes),
        )