class Troca:
    def __init__(self, id, jogador_origem, jogador_destino, pokemon_oferecido, pokemon_desejado, status=False):
        self.id = id
        self.jogador_origem = jogador_origem
        self.jogador_destino = jogador_destino
        self.pokemon_oferecido = pokemon_oferecido
        self.pokemon_desejado = pokemon_desejado
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "jogador_origem": self.jogador_origem.id,
            "jogador_destino": self.jogador_destino.id,
            "pokemon_oferecido": self.pokemon_oferecido.nome,
            "pokemon_desejado": self.pokemon_desejado.nome,
            "status": self.status
        }