
class Pokemon:
    def __init__(self, id, nome, status, nivel):
        self.id = id
        self.nome = nome
        self.status = status
        self.nivel = nivel

    def atacar(self):
        return f"{self.nome} atacou!"

class PokemonShiny(Pokemon):
    def brilhar(self):
        return f"{self.nome} está brilhando!"

class PokemonMega(Pokemon):
    def mega_evoluir(self):
        return f"{self.nome} mega evoluiu!"
