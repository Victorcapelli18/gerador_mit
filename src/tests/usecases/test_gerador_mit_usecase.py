import unittest
from unittest.mock import Mock, patch, MagicMock, call
import os
import tempfile
import json
from src.usecases.generate_mit_json import GeradorMitUseCase
from src.domain.entities.mit_entity import Mit, PeriodoApuracao, DadosIniciais, Debitos


class TestGeradorMitUseCase(unittest.TestCase):
    def setUp(self):
        # Criar diretório temporário para os testes
        self.temp_dir = tempfile.mkdtemp()
        
        # Mockup do schema
        self.schema = {"required": ["PeriodoApuracao", "DadosIniciais", "Debitos"]}
        
        # Mockup do repository
        self.repository = Mock()
        
        # Mockup do callback de progresso
        self.progress_callback = Mock()
        
        # Criar instância do caso de uso
        self.usecase = GeradorMitUseCase(
            self.repository,
            self.temp_dir,
            self.schema,
            progress_callback=self.progress_callback
        )
        
        # Criar um objeto Mit simulado
        self.mock_mit = self._criar_mock_mit()
        
    def tearDown(self):
        # Limpar arquivos temporários
        for arquivo in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, arquivo))
        os.rmdir(self.temp_dir)
        
    def _criar_mock_mit(self):
        """Cria um objeto Mit para testes."""
        mock_mit = Mock(spec=Mit)
        
        # Configurar o comportamento de dict()
        mock_mit.dict.return_value = {
            "PeriodoApuracao": {"MesApuracao": 3, "AnoApuracao": 2025},
            "DadosIniciais": {"SemMovimento": False},
            "Debitos": {"balanco_lucro_real": True}
        }
        
        # Configurar o comportamento de periodo_apuracao
        mock_periodo = Mock(spec=PeriodoApuracao)
        mock_periodo.ano_apuracao = 2025
        mock_periodo.mes_apuracao = 3
        mock_mit.periodo_apuracao = mock_periodo
        
        # Configurar o método gerar_nome_arquivo
        mock_mit.gerar_nome_arquivo.return_value = "EMPRESA_TESTE--MIT--202503.json"
        
        return mock_mit
    
    @patch('src.usecases.generate_mit_json.validar_json')
    def test_executar_sem_empresas(self, mock_validar_json):
        """Testa o comportamento quando não há empresas."""
        # Configurar o repository para retornar uma lista vazia
        self.repository.obter_empresas.return_value = []
        
        # Executar o caso de uso
        self.usecase.executar()
        
        # Verificar chamadas
        self.repository.obter_empresas.assert_called_once()
        self.repository.carregar_dados.assert_not_called()
        mock_validar_json.assert_not_called()
        
    @patch('src.usecases.generate_mit_json.validar_json')
    def test_executar_com_empresa_valida(self, mock_validar_json):
        """Testa o comportamento com uma empresa válida."""
        # Configurar o repository
        self.repository.obter_empresas.return_value = ["EMPRESA_TESTE"]
        self.repository.carregar_dados.return_value = self.mock_mit
        
        # Configurar o validador para retornar verdadeiro
        mock_validar_json.return_value = (True, None)
        
        # Executar o caso de uso
        self.usecase.executar()
        
        # Verificar chamadas
        self.repository.obter_empresas.assert_called_once()
        self.repository.carregar_dados.assert_called_once_with("EMPRESA_TESTE")
        self.mock_mit.dict.assert_called_once_with(by_alias=True)
        mock_validar_json.assert_called_once()
        
        # Verificar se o arquivo foi criado
        caminho_arquivo = os.path.join(self.temp_dir, "EMPRESA_TESTE--MIT--202503.json")
        self.assertTrue(os.path.exists(caminho_arquivo))
        
        # Verificar o conteúdo do arquivo
        with open(caminho_arquivo, 'r') as f:
            conteudo = json.load(f)
        self.assertEqual(conteudo["PeriodoApuracao"]["MesApuracao"], 3)
        
    @patch('src.usecases.generate_mit_json.validar_json')
    def test_progresso_atualizado(self, mock_validar_json):
        """Testa se o progresso é atualizado corretamente."""
        # Configurar o repository
        self.repository.obter_empresas.return_value = ["EMPRESA1", "EMPRESA2"]
        self.repository.carregar_dados.return_value = self.mock_mit
        
        # Configurar o validador para retornar verdadeiro
        mock_validar_json.return_value = (True, None)
        
        # Executar o caso de uso
        self.usecase.executar()
        
        # Verificar as chamadas ao callback de progresso
        expected_calls = [
            call(0.0),    # Início da EMPRESA1
            call(0.5),    # Fim da EMPRESA1 
            call(0.5),    # Início da EMPRESA2
            call(1.0),    # Fim da EMPRESA2
            call(1.0)     # Fim da execução
        ]
        self.progress_callback.assert_has_calls(expected_calls)
        
    @patch('src.usecases.generate_mit_json.validar_json')
    def test_erro_validacao(self, mock_validar_json):
        """Testa o comportamento quando há erro de validação."""
        # Configurar o repository
        self.repository.obter_empresas.return_value = ["EMPRESA_INVALIDA"]
        self.repository.carregar_dados.return_value = self.mock_mit
        
        # Configurar o validador para retornar falso (erro)
        erro_mock = Mock()
        erro_mock.message = "Erro de validação"
        mock_validar_json.return_value = (False, erro_mock)
        
        # Executar o caso de uso
        self.usecase.executar()
        
        # Verificar chamadas
        mock_validar_json.assert_called_once()
        
        # Verificar se o arquivo de erro foi criado
        caminho_erro = os.path.join(self.temp_dir, "erros_validacao.txt")
        self.assertTrue(os.path.exists(caminho_erro))
        
        # Verificar o conteúdo do arquivo de erro
        with open(caminho_erro, 'r') as f:
            conteudo = f.read()
        self.assertIn("Erro de validação para EMPRESA_INVALIDA", conteudo)


if __name__ == "__main__":
    unittest.main() 