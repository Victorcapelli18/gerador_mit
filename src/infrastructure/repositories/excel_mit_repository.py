from src.infrastructure.adapters.excel_adapter import ExcelAdapter
from src.infrastructure.mappers.excel_mapper import ExcelMapper
from src.domain.entities.mit_entity import Mit


class ExcelMitRepository:
    def __init__(self, caminho_arquivo: str):
        self.adapter = ExcelAdapter()
        self.mapper = ExcelMapper()
        # self.dados é um Dict[str, List[Dict]] carregado pelo adapter
        self.dados = self.adapter.carregar_planilha_excel(caminho_arquivo)

    def obter_empresas(self) -> list[str]:
        # Mais robusto para o caso de "DadosIniciais" não existir ou linha sem "Empresa"
        return list(set(
            linha["Empresa"] 
            for linha in self.dados.get("DadosIniciais", []) 
            if "Empresa" in linha
        ))
    
    def carregar_dados(self, empresa: str) -> Mit:
        # Filtro para os dados da empresa especificada
        # Usar .get() no dicionário da linha para segurança caso a coluna "Empresa" falte em alguma linha por erro
        filtro_empresa = lambda linha_dict: linha_dict.get("Empresa") == empresa

        # Filtrar os dados de cada aba relevante para a empresa especificada
        dados_periodo_apuracao_empresa = [
            linha for linha in self.dados.get("PeriodoApuracao", []) if filtro_empresa(linha)
        ]
        dados_iniciais_empresa = [
            linha for linha in self.dados.get("DadosIniciais", []) if filtro_empresa(linha)
        ]
        # Para Débitos e ListaSuspensoes, pegamos todas as linhas da empresa
        debitos_empresa = [
            linha for linha in self.dados.get("Debitos", []) if filtro_empresa(linha)
        ]
        lista_suspensoes_empresa = [
            linha for linha in self.dados.get("ListaSuspensoes", []) if filtro_empresa(linha)
        ]
        
        # O ExcelMapper espera um dicionário onde as chaves são nomes de abas
        # e os valores são listas de dicionários (linhas)
        dados_formatados_para_mapper = {
            "PeriodoApuracao": dados_periodo_apuracao_empresa,
            "DadosIniciais": dados_iniciais_empresa,
            "Debitos": debitos_empresa,
            "ListaSuspensoes": lista_suspensoes_empresa
        }

        # Chama o método map_to_mit do mapper para obter o objeto Mit completo
        mit_objeto = self.mapper.map_to_mit(dados_formatados_para_mapper)
        
        return mit_objeto