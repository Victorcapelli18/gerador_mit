import json
import os
import re
from collections import Counter
from src.infrastructure.adapters.json_validator import validar_json
from src.domain.entities.mit_entity import Mit
from src.domain.repositories.mit_repository_interface import MitRepositoryInterface
from typing import Optional, Callable, Dict

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

        # Dicionário para armazenar os dados carregados de cada empresa
        dados_empresas = {}
        # Mapeamento de empresas para CNPJs
        empresa_cnpj_map = {}
        
        # Primeira passagem: carrega os dados e extrai CNPJs
        print(f"Carregando dados de {len(empresas)} empresas...")
        for empresa in empresas:
            try:
                mit_obj = self.repository.carregar_dados(empresa)
                if mit_obj:
                    dados_empresas[empresa] = mit_obj
                    # Extrair CNPJ
                    cnpj = self._extrair_cnpj_de_debitos(mit_obj)
                    if cnpj:
                        empresa_cnpj_map[empresa] = cnpj
            except Exception as e:
                print(f"Erro ao carregar dados da empresa {empresa}: {str(e)}")
        
        # Segunda passagem: processa e gera os arquivos
        total_empresas = len(dados_empresas)
        if total_empresas == 0:
            print("Nenhuma empresa com dados válidos encontrada.")
            return
            
        print(f"Processando {total_empresas} empresas...")
        for idx, (nome_empresa, mit_obj) in enumerate(dados_empresas.items()):
            try:
                # Atualiza o progresso
                if self.progress_callback:
                    progresso = idx / total_empresas
                    self.progress_callback(progresso)
                
                # Validar o JSON contra o schema
                mit_dict_para_validar = mit_obj.dict(by_alias=True)
                valido, erro_val = validar_json(mit_dict_para_validar, self.json_schema)
                
                if not valido:
                    self._registrar_erro_validacao(nome_empresa, erro_val)
                    continue

                # Obter CNPJ do mapeamento
                cnpj = empresa_cnpj_map.get(nome_empresa)
                origem_cnpj = "mapeamento inicial"
                
                # Se não encontrou no mapeamento, tenta no campo cnpj de dados_iniciais
                if not cnpj and mit_obj.dados_iniciais.cnpj:
                    cnpj_limpo = re.sub(r'[^0-9]', '', mit_obj.dados_iniciais.cnpj)
                    if len(cnpj_limpo) >= 8:
                        cnpj = cnpj_limpo
                        origem_cnpj = "dados_iniciais.cnpj"
                
                # Se ainda não encontrou, usa o método fallback (busca nos débitos e outros campos)
                if not cnpj:
                    cnpj = self._obter_cnpj_fallback(mit_obj, nome_empresa)
                    origem_cnpj = "fallback"
                
                # Log para depuração
                print(f"CNPJ para {nome_empresa}: {cnpj} (origem: {origem_cnpj})")

                # Usar o método da entidade para gerar o nome do arquivo
                nome_arquivo = mit_obj.gerar_nome_arquivo(cnpj)
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
    
    def _extrair_cnpj_de_debitos(self, mit_obj: Mit) -> Optional[str]:
        """
        Extrai o CNPJ dos débitos da entidade Mit.
        
        Args:
            mit_obj: Objeto Mit contendo os débitos.
            
        Returns:
            CNPJ extraído ou None se não encontrado.
        """
        cnpjs_encontrados = []
        
        # Primeiro, verifica se há um CNPJ nos dados iniciais
        if mit_obj.dados_iniciais.cnpj:
            cnpj_limpo = re.sub(r'[^0-9]', '', str(mit_obj.dados_iniciais.cnpj))
            if len(cnpj_limpo) >= 11:  # CNPJ tem pelo menos 11 dígitos
                cnpjs_encontrados.append(cnpj_limpo)
                print(f"CNPJ encontrado nos dados_iniciais: {cnpj_limpo}")
        
        # Depois, verifica nos débitos
        for imposto in [
            mit_obj.debitos.irpj, mit_obj.debitos.csll, mit_obj.debitos.irrf, 
            mit_obj.debitos.ipi, mit_obj.debitos.iof, mit_obj.debitos.pis_pasep, 
            mit_obj.debitos.cofins, mit_obj.debitos.contribuicoes_diversas, mit_obj.debitos.cpss
        ]:
            for debito in imposto.lista_debitos:
                if debito.cnpj_scp:
                    cnpj_limpo = re.sub(r'[^0-9]', '', str(debito.cnpj_scp))
                    if len(cnpj_limpo) >= 11:  # CNPJ tem pelo menos 11 dígitos
                        cnpjs_encontrados.append(cnpj_limpo)
                        print(f"CNPJ encontrado em débito: {cnpj_limpo}")
        
        # Se encontrou algum CNPJ, retorna o que aparece com mais frequência
        if cnpjs_encontrados:
            # Contagem de ocorrências
            contador = Counter(cnpjs_encontrados)
            # Retorna o CNPJ mais frequente
            cnpj_mais_frequente = contador.most_common(1)[0][0]
            return cnpj_mais_frequente
            
        return None
    
    def _obter_cnpj_fallback(self, mit_obj: Mit, nome_empresa: str) -> str:
        """
        Método de fallback para obter o CNPJ quando não está disponível no mapeamento.
        
        Args:
            mit_obj: Objeto Mit que contém os dados da empresa.
            nome_empresa: Nome da empresa.
            
        Returns:
            CNPJ ou string formatada para o nome do arquivo.
        """
        # Tenta encontrar o CNPJ nos débitos
        cnpj = self._extrair_cnpj_de_debitos(mit_obj)
        if cnpj:
            print(f"Fallback - CNPJ encontrado via _extrair_cnpj_de_debitos: {cnpj}")
            return cnpj
        
        # Procura por padrões de CNPJ no nome da empresa
        padrao_cnpj = r'(\d{2}[\.\s]?\d{3}[\.\s]?\d{3}[\/\.\s]?\d{4}[-\.\s]?\d{2})'
        match = re.search(padrao_cnpj, nome_empresa)
        if match:
            cnpj_encontrado = match.group(1)
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj_encontrado))
            if len(cnpj_limpo) >= 8:
                print(f"Fallback - CNPJ extraído do nome via regex: {cnpj_limpo}")
                return cnpj_limpo[:8]  # Retorna os 8 primeiros dígitos (CNPJ raiz)
        
        # Verifica nos detalhes da empresa
        nome_limpo = nome_empresa.lower()
        if any(termo in nome_limpo for termo in ["cnpj", "cpf", "mei", "individual"]):
            # Extrai possíveis números que podem ser um CNPJ/CPF do nome
            numeros_extraidos = re.findall(r'\d+', nome_empresa)
            for num in numeros_extraidos:
                if len(num) >= 8:
                    print(f"Fallback - CNPJ potencial extraído do nome: {num}")
                    return num[:8]  # Usa os primeiros 8 dígitos
        
        # Se não encontrou CNPJ, tenta converter o nome da empresa para um formato numérico
        numeros = re.sub(r'[^0-9]', '', nome_empresa)
        if len(numeros) >= 8:
            print(f"Fallback - Usando números do nome da empresa: {numeros[:8]}")
            return numeros[:8]  # Usa os primeiros 8 dígitos
        
        # Se não conseguir obter um CNPJ válido, usa um padrão fictício baseado no nome
        # padronizando para evitar caracteres especiais no nome do arquivo
        print(f"Fallback - Usando padrão 00000000 para: {nome_empresa}")
        nome_seguro = re.sub(r'[^a-zA-Z0-9]', '', nome_empresa)
        return "00000000"  # Usa um padrão fixo
            
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