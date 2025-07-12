import json
import os
import re
from collections import Counter
from src.infrastructure.adapters.json_validator import validar_json
from src.domain.entities.mit_entity import MitEntity
from src.domain.repositories.mit_repository_interface import MitRepositoryInterface
from typing import Optional, Callable, Dict

class GeradorMitUseCase:
    def __init__(self, repository: MitRepositoryInterface, pasta_saida: str, json_schema: dict,
                 progress_callback: Optional[Callable[[float], None]] = None):
        self.repository = repository
        self.pasta_saida = pasta_saida
        self.json_schema = json_schema
        self.erros_registrados = set()
        self.progress_callback = progress_callback
        os.makedirs(pasta_saida, exist_ok=True)

    def executar(self):
        empresas = self.repository.obter_empresas()
        if not empresas:
            print("Nenhuma empresa encontrada para processar.")
            return
        
        dados_empresas = {}
        empresa_cnpj_map = {}

        print(f"Carregando dados de {len(empresas)} empresas...")
        for empresa in empresas:
            try:
                mit_obj = self.repository.carregar_dados(empresa)
                if mit_obj:
                    dados_empresas[empresa] = mit_obj
                    cnpj = self._extrair_cnpj_de_debitos(mit_obj)
                    if cnpj:
                        empresa_cnpj_map[empresa] = cnpj
            except Exception as e:
                print(f"Erro ao carregar dados da empresa {empresa}: {str(e)}")

        total_empresas = len(dados_empresas)
        if total_empresas == 0:
            print("Nenhuma empresa com dados validos encontrada.")
            return
        
        print(f"Processando {total_empresas} empresas...")
        for idx, (nome_empresa, mit_obj) in enumerate(dados_empresas.items()):
            try:
                if self.progress_callback:
                    progresso = idx / total_empresas
                    self.progress_callback(progresso)

                mit_dict_para_validar = mit_obj.dict(by_alias=True)
                valido, erro_val = validar_json(mit_dict_para_validar, self.json_schema)

                if not valido:
                    self._registrar_erro_validacao(nome_empresa, erro_val)
                    continue

                cnpj = empresa_cnpj_map.get(nome_empresa)
                origem_cnpj = "mapeamento inicial"

                if not cnpj and mit_obj.dados_iniciais.cnpj:
                    cnpj_limpo = re.sup(r'[^0-9]', '', mit_obj.dados_iniciais.cnpj)
                    if len(cnpj_limpo) >= 8:
                        cnpj = cnpj_limpo
                        origem_cnpj = "dados_iniciais.cnpj"

                if not cnpj:
                    cnpj = self._obter_cnpj_fallback(mit_obj, nome_empresa)
                    origem_cnpj = "fallback"

                print(f"CNPJ para {nome_empresa}: {cnpj} (origem: {origem_cnpj})")

                nome_arquivo = mit_obj.gerar_nome_arquivo(cnpj)
                caminho_arquivo_saida = os.path.join(self.pasta_saida, nome_arquivo)

                with open(caminho_arquivo_saida, 'w', encoding='utf-8') as f_json:
                    json.dump(mit_dict_para_validar, f_json, indent=4, ensure_ascii=False)

                print(f"JSON gerado para {nome_empresa} em {caminho_arquivo_saida}")

            except Exception as e:
                self._registrar_erro_critico(nome_empresa, e)

            if self.progress_callback:
                progresso = (idx + 1) / total_empresas
                self.progress_callback(progresso)

        if self.progress_callback:
            self.progress_callback(1.0)

    def _extrair_cnpj_de_debitos(self, mit_obj: MitEntity) -> Optional[str]:

        cnpjs_encontrados = []

        if mit_obj.dados_iniciais.cnpj:
            cnpj_limpo = re.sub(r'[^0-9]', '', str(mit_obj.dados_iniciais.cnpj))
            if len(cnpj_limpo) >= 11:
                cnpjs_encontrados.append(cnpj_limpo)
                print(f"CNPJ encontrado nos dados_inciais: {cnpj_limpo}")

        for imposto in [
            mit_obj.debitos.irpj, mit_obj.debitos.csll, mit_obj.debitos.irrf, 
            mit_obj.debitos.ipi, mit_obj.debitos.iof, mit_obj.debitos.pis_pasep, 
            mit_obj.debitos.cofins, mit_obj.debitos.contribuicoes_diversas, mit_obj.debitos.cpss
        ]:
            for debito in imposto.lista_debitos:
                if debito.cnpj_scp:
                    cnpj_limpo = re.sub(r'[^0-9]', '', str(debito.cnpj_scp))
                    if len(cnpj_limpo) >= 11:
                        cnpjs_encontrados.append(cnpj_limpo)
                        print(f"CNPJ encontrado em débito: {cnpj_limpo}")

        if cnpjs_encontrados:
            contador = Counter(cnpjs_encontrados)
            cnpj_mais_frequente = contador.most_common(1)[0][0]
            return cnpj_mais_frequente
        
        return None
    
    def _obter_cnpj_fallback(self, mit_obj: MitEntity, nome_empresa: str) -> str:
        cnpj = self._extrair_cnpj_de_debitos(mit_obj)
        if cnpj:
            print(f"Fallback - CNPJ encontrado via _extrair_cnpj_de_debitos: {cnpj}")
            return cnpj
        
        padrao_cnpj = r'(\d{2}[\.\s]?\d{3}[\.\s]?\d{3}[\/\.\s]?\d{4}[-\.\s]?\d{2})'
        match = re.search(padrao_cnpj, nome_empresa)
        if match:
            cnpj_encontrado = match.group(1)
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj_encontrado))
            if len(cnpj_limpo) >= 8:
                print(f"Fallback - CNPJ extraído do nome via regex: {cnpj_limpo}")
                return cnpj_limpo[:8]
            
        nome_limpo = nome_empresa.lower()
        if any(termo in nome_limpo for termo in ["cnpj", "cpf", "mei", "individual"]):
            numeros_extraidos = re.findall(r'\d+', nome_empresa)
            for num in numeros_extraidos:
                if len(num) >= 8:
                    print(f"Fallback - CNPJ potencial extraído do nome: {num}")
                    return num[:8]
        
        numeros = re.sub(r'\D', '', nome_empresa)
        if len(numeros) >= 8:
            print(f"Fallback - Usando os números do nome da empresa: {numeros[:8]}")
            return numeros[:8]
        
        print(f"Fallback - Usando padrão 00000000 para: {nome_empresa}")
        nome_seguro = re.sub(r'[^a-zA-Z0-9]', '', nome_empresa)
        return "00000000"  # Usa um padrão fixo
    
    def _registrar_erro_validacao(self, nome_empresa: str, erro_val) -> None:
        """Registra um erro de validação em arquivo"""
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
        """Registra um erro critico em arquivo"""
        erro_msg = f"Erro critico ao processar empresa {nome_empresa}: {str(erro)}"
        print(erro_msg)

        caminho_erro_critico = os.path.join(self.pasta_saida, "erros_criticos_processamento.txt")
        if erro_msg not in self.erros_registrados:
            self.erros_registrados.add(erro_msg)
            with open(caminho_erro_critico, "a", encoding="utf-8") as f_critico:
                f_critico.write(erro_msg + "\n")


                