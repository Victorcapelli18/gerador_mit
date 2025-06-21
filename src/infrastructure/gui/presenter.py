from src.usecases.generate_mit_json import GeradorMitUseCase
from src.domain.repositories.mit_repository_interface import MitRepositoryInterface
from src.infrastructure.repositories.excel_mit_repository import ExcelMitRepository
from typing import Protocol, Optional, Callable


class ViewInterface(Protocol):
    """Interface para a visualização da aplicação."""
    
    def mostrar_erro(self, mensagem: str) -> None:
        """Mostra uma mensagem de erro para o usuário."""
        ...
        
    def mostrar_sucesso(self, mensagem: str) -> None:
        """Mostra uma mensagem de sucesso para o usuário."""
        ...
        
    def atualizar_progresso(self, valor: float) -> None:
        """Atualiza o valor da barra de progresso."""
        ...
        
    def mostrar_progresso(self) -> None:
        """Torna a barra de progresso visível."""
        ...
        
    def esconder_progresso(self) -> None:
        """Esconde a barra de progresso."""
        ...


class MitPresenter:
    """
    Presenter que coordena a interação entre a view e os casos de uso.
    Segue o padrão MVP (Model-View-Presenter).
    """

    def __init__(self, view: ViewInterface):
        self.view = view
        self.excel_path: Optional[str] = None
        self.output_path: Optional[str] = None
        self.schema: Optional[dict] = None

    def definir_schema(self, schema: dict) -> None:
        """Define o schema para validacao do JSON."""
        self.schema = schema

    def definir_caminho_excel(self, caminho: str) -> None:
        """Define o caminho do arquivo Excel."""
        self.excel_path = caminho
    
    def definir_pasta_saida(self, caminho: str) -> None:
        """"Define o caminho da pasta de saída."""
        self.output_path = caminho
        
    def gerar_json(self) -> None:
        """Inicia o processao de geracao de JSON."""
        if not self.excel_path or not self.output_path or not self.schema:
            self.view.mostrar_erro("Selecione o arquivo e a pasta de saída!")
            return
        
        try:
            self.view.mostrar_progresso()
            self.view.atualizar_progresso(0)

            # Funcao de callback para atualizacao do progresso
            def atualizar_progresso(valor: float) -> None:
                self.view.atualizar_progresso(valor)

            # Criacao do repositorio e caso de uso
            repository: MitRepositoryInterface = ExcelMitRepository(self.excel_path)
            usecase = GeradorMitUseCase(
                repository,
                self.output_path,
                self.schema,
                progress_callback=atualizar_progresso
            )

            # Execução do caso de uso
            usecase.executar()

            self.view.mostrar_sucesso("Arquivos gerados com sucesso!")

        except Exception as e:
            self.view.mostrar_erro(f"Falha na geração: {str(e)}")
        
        finally:
            self.view.esconder_progresso()