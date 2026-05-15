
class ValidadorBase:
    def __init__(self, proximo=None):
        self._proximo = proximo

    def validar(self, troca):
        if self._proximo:
            return self._proximo.validar(troca)
        return True

class ValidadorNivel(ValidadorBase):
    def validar(self, troca):
        if troca.pokemon_oferecido.nivel < troca.pokemon_desejado.nivel:
            print("Nível insuficiente para troca.")
            return False
        return super().validar(troca)

class ValidadorStatus(ValidadorBase):
    def validar(self, troca):
        if troca.pokemon_oferecido.status != "disponivel":
            print("Pokémon não está disponível para troca.")
            return False
        return super().validar(troca)
