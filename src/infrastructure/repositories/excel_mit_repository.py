import pandas as pd
from src.infrastructure.adapters.excel_adpter import ExcelAdapter
from src.infrastructure.mappers.excel_mapper import ExcelMapper


class ExcelMitRepository:
    def __init__(self, caminho_arquivo: str):
        self.adapter = ExcelAdapter()
        self.mapper = ExcelMapper()
        self.dados = self.adapter.carregar_planilha_excel(caminho_arquivo)


    def obter_empresas(self) -> list[str]:
        return list({linha["empresa"] for linha in self.dados["DadosIniciais"]})
    

    def carregar_dados(self, empresa: str):
        filtro = lambda d: d["empresa"] == empresa

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
    



# if __name__ == "__main__":
#     caminho = r"C:\Users\victo\OneDrive\Documentos\json_tests\planilha_mit_final_v5.xlsx"
#     repo = ExcelMitRepository(caminho)



#     empresas = repo.obter_empresas()
#     print(empresas)


#     if empresas:
#         empresa = empresas[0]
#         print(f"\n=== Dados da empresa: {empresa} ===")
#         periodo, dados_iniciais, debitos, suspensoes = repo.carregar_dados(empresa)

#         print("\n-> Período de Apuração:")
#         print(periodo)

#         print("\n-> Dados Iniciais:")
#         print(dados_iniciais)

#         print("\n-> Débitos (head):")
#         print(debitos.head())

#         print("\n-> Suspensões (head):")
#         print(suspensoes.head())