from src.infrastructure.adapters.excel_adapter import ExcelAdapter
from src.infrastructure.mappers.excel_mapper import ExcelMapper
from src.domain.entities.mit_entity import MitEntity
from src.domain.repositories.mit_repository_interface import MitRepositoryInterface
from typing import List, Optional


class ExcelMitRepository(MitRepositoryInterface):
    def __init__(self, caminho_arquivo: str):
        self.adapter = ExcelAdapter()
        self.mapper = ExcelMapper()
        self.dados = self.adapter.carregar_planilha_excel(caminho_arquivo)


    def obter_empresas(self) -> List[str]:
        return list(set(
            linha["Empresa"]
            for linha in self.dados.get("DadosIniciais", [])
            if "Empresa" in linha
        ))
    
    def carregar_dados(self, empresa: str) -> Optional[MitEntity]:
        filtro_empresa = lambda linha_dict: linha_dict.get("Empresa") == empresa

        dados_periodo_apuracao_empresa = [
            linha for linha in self.dados.get("PeriodoApuracao", []) if filtro_empresa(linha)
        ]
        dados_iniciais_empresa = [
            linha for linha in self.dados.get("DadosIniciais", []) if filtro_empresa(linha)
        ]
        debitos_empresa = [
            linha for linha in self.dados.get("Debitos", []) if filtro_empresa(linha)
        ]
        lista_suspensoes_empresa = [
            linha for linha in self.dados.get("ListaSuspensoes", []) if filtro_empresa(linha)
        ]
        
        dados_formatados_para_mapper = {
            "PeriodoApuracao": dados_periodo_apuracao_empresa,
            "DadosIniciais": dados_iniciais_empresa,
            "Debitos": debitos_empresa,
            "ListaSuspensoes": lista_suspensoes_empresa
        }

        mit_objeto = self.mapper.map_to_mit(dados_formatados_para_mapper)
        
        return mit_objeto