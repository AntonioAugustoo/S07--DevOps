
from abc import ABC, abstractmethod

class INotificacao(ABC):
    @abstractmethod
    def notificar(self, jogador, mensagem: str):
        pass
