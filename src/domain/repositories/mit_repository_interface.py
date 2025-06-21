from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.mit_entity import MitEntity


class MitRepositoryInterface(ABC):
    @abstractmethod
    def obter_empresas(self) -> List[str]:
        """Obtém a lista de CNPJs das empresas."""
        pass

    @abstractmethod
    def carregar_dados(self, empresa: str) -> Optional[MitEntity]:
        """
        Carrega os dados de uma empresa específica e retorna um objeto Mit.
        
        Args:
            empresa: Nome da empresa cujos dados serão carregados.
            
        Returns:
            Um objeto Mit com todos os dados preenchidos ou None se não for possível carregar.
        """
        pass 