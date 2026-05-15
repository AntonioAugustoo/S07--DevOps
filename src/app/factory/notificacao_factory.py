
from app.notifications.notificacao_jogador import NotificacaoJogador

class NotificacaoFactory:
    def criar_notificacao(self):
        return NotificacaoJogador()
