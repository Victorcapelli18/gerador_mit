import json
import os
from src.infrastructure.adapters.json_validator import validar_json
# from src.domain.services.gerador_mit_service import GeradorService # Removido
from src.domain.entities.mit_entity import Mit # PeriodoApuracao não é mais necessário aqui diretamente
from src.domain.repositories.mit_repository_interface import MitRepositoryInterface
from typing import Optional, Callable

class GeradorMitUseCase:
    def __init__(self, repository: MitRepositoryInterface, pasta_saida: str, json_schema: dict, 
                 progress_callback: Optional[Callable[[float], None]] = None):
        self.repository = repository
        self.pasta_saida = pasta_saida
        self.json_schema = json_schema
        self.erros_registrados = set()
        # self.service = GeradorService() # Removido
        self.progress_callback = progress_callback
        os.makedirs(pasta_saida, exist_ok=True)

    def executar(self):
        empresas = self.repository.obter_empresas()
        if not empresas:
            print("Nenhuma empresa encontrada para processar.")
            return

        total_empresas = len(empresas)
        for idx, nome_empresa in enumerate(empresas):
            try:
                # Atualiza o progresso antes de processar cada empresa
                if self.progress_callback:
                    progresso = idx / total_empresas
                    self.progress_callback(progresso)
                
                # O repositório retorna o objeto Mit completo
                mit_obj = self.repository.carregar_dados(nome_empresa)

                if not mit_obj:
                    print(f"Não foi possível carregar dados para a empresa: {nome_empresa}")
                    continue

                # Validar o JSON contra o schema
                mit_dict_para_validar = mit_obj.dict(by_alias=True)
                valido, erro_val = validar_json(mit_dict_para_validar, self.json_schema)
                
                if not valido:
                    self._registrar_erro_validacao(nome_empresa, erro_val)
                    continue

                # Usar o método da entidade para gerar o nome do arquivo
                nome_arquivo = mit_obj.gerar_nome_arquivo(nome_empresa)
                caminho_arquivo_saida = os.path.join(self.pasta_saida, nome_arquivo)

                # Salvar o arquivo JSON
                with open(caminho_arquivo_saida, 'w', encoding='utf-8') as f_json:
                    json.dump(mit_dict_para_validar, f_json, indent=4, ensure_ascii=False)
                
                print(f"JSON gerado para {nome_empresa} em {caminho_arquivo_saida}")

            except Exception as e:
                self._registrar_erro_critico(nome_empresa, e)
            
            # Atualiza o progresso após processar cada empresa
            if self.progress_callback:
                progresso = (idx + 1) / total_empresas
                self.progress_callback(progresso)
                
        # Garante que chegue a 100% no final
        if self.progress_callback:
            self.progress_callback(1.0)
            
    def _registrar_erro_validacao(self, nome_empresa: str, erro_val) -> None:
        """Registra um erro de validação em arquivo."""
        msg = f"Erro de validação para {nome_empresa}: {str(erro_val)}"
        if hasattr(erro_val, 'message'):
            msg = f"Erro de validação para {nome_empresa}: {erro_val.message}"
        
        if msg not in self.erros_registrados:
            self.erros_registrados.add(msg)
            caminho_erro = os.path.join(self.pasta_saida, "erros_validacao.txt")
            with open(caminho_erro, "a", encoding="utf-8") as f_erro:
                f_erro.write(msg + "\n")
        print(msg)
        
    def _registrar_erro_critico(self, nome_empresa: str, erro: Exception) -> None:
        """Registra um erro crítico em arquivo."""
        erro_msg = f"Erro crítico ao processar empresa {nome_empresa}: {str(erro)}"
        print(erro_msg)
        
        caminho_erro_critico = os.path.join(self.pasta_saida, "erros_criticos_processamento.txt")
        if erro_msg not in self.erros_registrados:
            self.erros_registrados.add(erro_msg)
            with open(caminho_erro_critico, "a", encoding="utf-8") as f_critico:
                f_critico.write(erro_msg + "\n")