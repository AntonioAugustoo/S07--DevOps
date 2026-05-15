from app.notifications.inotificacao import INotificacao

class NotificacaoDecorator:
    def init(self, notificacao: INotificacao):
        self._notificacao = notificacao

    def notificar(self, jogador, mensagem):
        print(f"[LOG] Enviando notificação: {mensagem}")
        self._notificacao.notificar(jogador, mensagem)