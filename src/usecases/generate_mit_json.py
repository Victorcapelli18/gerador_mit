import json
import os
from src.infrastructure.adapters.json_validator import validar_json
# from src.domain.services.gerador_mit_service import GeradorService # Removido
from src.domain.entities.mit_entity import Mit # PeriodoApuracao não é mais necessário aqui diretamente

class GeradorMitUseCase:
    def __init__(self, repository, pasta_saida: str, json_schema: dict):
        self.repository = repository
        self.pasta_saida = pasta_saida
        self.json_schema = json_schema
        self.erros_registrados = set()
        # self.service = GeradorService() # Removido
        os.makedirs(pasta_saida, exist_ok=True)

    def executar(self):
        empresas = self.repository.obter_empresas()
        if not empresas:
            print("Nenhuma empresa encontrada para processar.")
            return

        for nome_empresa in empresas: # Renomeado 'nome' para 'nome_empresa' para clareza
            try:
                # O repositório agora retorna o objeto Mit completo
                mit_obj = self.repository.carregar_dados(nome_empresa)

                if not mit_obj: # Adicionando uma verificação caso o mapper retorne None (embora ele levante erro atualmente)
                    print(f"Não foi possível carregar dados para a empresa: {nome_empresa}")
                    continue

                # A construção manual do mit_obj e o uso do service foram removidos
                # pois mit_obj já é a entidade Mit completa.

                # Usar mit_obj.model_dump() para Pydantic v2+ ou mit_obj.dict() para v1
                # Assumindo Pydantic v1 com base no uso de .dict(by_alias=True)
                mit_dict_para_validar = mit_obj.dict(by_alias=True)
                
                valido, erro_val = validar_json(mit_dict_para_validar, self.json_schema)
                
                if not valido:
                    msg = f"Erro de validação para {nome_empresa}: {str(erro_val)}" # Usar str(erro_val) pois o erro pode não ter .message
                    if hasattr(erro_val, 'message'): # Checagem se tem o atributo message
                        msg = f"Erro de validação para {nome_empresa}: {erro_val.message}"
                    
                    if msg not in self.erros_registrados:
                        self.erros_registrados.add(msg)
                        caminho_erro = os.path.join(self.pasta_saida, "erros_validacao.txt")
                        with open(caminho_erro, "a", encoding="utf-8") as f_erro:
                            f_erro.write(msg + "\\n")
                    print(msg) # Adicionado print para feedback imediato no console
                    continue

                # Construção do nome do arquivo JSON
                ano = mit_obj.periodo_apuracao.ano_apuracao
                mes = str(mit_obj.periodo_apuracao.mes_apuracao).zfill(2)
                periodo_str = f"{ano}{mes}"
                
                nome_arquivo = f"{nome_empresa}--MIT--{periodo_str}.json"
                caminho_arquivo_saida = os.path.join(self.pasta_saida, nome_arquivo)

                with open(caminho_arquivo_saida, 'w', encoding='utf-8') as f_json:
                    # Usar mit_obj.model_dump_json() para Pydantic v2+ ou json.dump(mit_obj.dict()) para v1
                    json.dump(mit_dict_para_validar, f_json, indent=4, ensure_ascii=False)
                
                print(f"JSON gerado para {nome_empresa} em {caminho_arquivo_saida}")

            except Exception as e:
                erro_msg = f"Erro crítico ao processar empresa {nome_empresa}: {str(e)}"
                print(erro_msg)
                # Logar também no arquivo de erros
                caminho_erro_critico = os.path.join(self.pasta_saida, "erros_criticos_processamento.txt")
                if erro_msg not in self.erros_registrados: # Evitar duplicar se já logado
                    self.erros_registrados.add(erro_msg)
                    with open(caminho_erro_critico, "a", encoding="utf-8") as f_critico:
                        f_critico.write(erro_msg + "\\n")