
from app.notifications.inotificacao import INotificacao

class NotificacaoNovoPokemon(INotificacao):
    def notificar_novo_pokemon(self, pokemon, mensagem: str):
        print(f"Notificação sobre {pokemon.nome}: {mensagem}")
