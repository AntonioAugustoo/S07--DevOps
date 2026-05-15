
from app.notifications.inotificacao import INotificacao

class NotificacaoJogador(INotificacao):
    def notificar(self, jogador, mensagem: str):
        print(f"Notificação para {jogador.nome}: {mensagem}")
