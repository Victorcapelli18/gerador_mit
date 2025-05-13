from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.mit_entity import Mit

class MitRepositoryInterface(ABC):
    """Interface para repositórios que fornecem dados para geração de arquivos MIT."""
    
    @abstractmethod
    def obter_empresas(self) -> List[str]:
        """Retorna uma lista de nomes de empresas disponíveis no repositório."""
        pass
    
    @abstractmethod
    def carregar_dados(self, empresa: str) -> Optional[Mit]:
        """
        Carrega os dados de uma empresa específica e retorna um objeto Mit.
        
        Args:
            empresa: Nome da empresa cujos dados serão carregados.
            
        Returns:
            Um objeto Mit com todos os dados preenchidos ou None se não for possível carregar.
        """
        pass 