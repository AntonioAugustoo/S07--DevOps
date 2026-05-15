class Jogador:
    def __init__(self, id, nome):
        self.pokemons = []
        self.propostas_recebidas = []
        self.id = id
        self.nome = nome

    def to_dict(self):
        print("DEBUG - Jogador:", self.id)
        print("Pokémons:", [type(p) for p in self.pokemons])
        print("Propostas recebidas:", [type(p) for p in self.propostas_recebidas])
        return {
            "id": self.id,
            "nome": self.nome,
            "pokemons": [p.nome for p in self.pokemons],
            "propostas_recebidas": [p.to_dict() if hasattr(p, "to_dict") else str(p) for p in self.propostas_recebidas]
        }