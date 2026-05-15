
from app.notifications.inotificacao import INotificacao

class GerenciadorDeTroca:
    def __init__(self, notificacao: INotificacao):
        self.notificacao = notificacao
        self.propostas = []

    def armazenar_proposta(self, troca):
        self.propostas.append(troca)

    def listar_propostas(self, jogador):
        return [p for p in self.propostas if p.jogador_origem.id == jogador.id or p.jogador_destino.id == jogador.id]

    def enviar_proposta(self, troca):
        self.armazenar_proposta(troca)
        self.notificacao.notificar(troca.jogador_destino, "Nova proposta de troca enviada!")

    def analisar_proposta(self, troca):
        troca.status = True
        self.notificacao.notificar(troca.jogador_origem, "Sua proposta foi aceita.")
        return True
