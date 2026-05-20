import unittest
from app.models.jogador import Jogador
from app.models.pokemon import Pokemon
from app.models.troca import Troca
from app.services.gerenciador_troca import GerenciadorDeTroca
from app.notifications.notificacao_jogador import NotificacaoJogador

class TesteModels(unittest.TestCase):

    def setUp(self):
        self.jogador1 = Jogador(1, "Ash")
        self.jogador2 = Jogador(2, "Misty")
        self.pokemon1 = Pokemon(1, "Pikachu", "disponivel", 10)
        self.pokemon2 = Pokemon(2, "Staryu", "disponivel", 8)
        self.troca = Troca(1, self.jogador1, self.jogador2, self.pokemon1, self.pokemon2)

    # ---- Jogador ----
    def test_jogador_to_dict(self):
        self.jogador1.pokemons.append(self.pokemon1)
        resultado = self.jogador1.to_dict()
        self.assertEqual(resultado["id"], 1)
        self.assertEqual(resultado["nome"], "Ash")
        self.assertIn("Pikachu", resultado["pokemons"])

    def test_jogador_to_dict_sem_pokemons(self):
        resultado = self.jogador1.to_dict()
        self.assertEqual(resultado["pokemons"], [])

    # ---- Troca ----
    def test_troca_to_dict(self):
        resultado = self.troca.to_dict()
        self.assertEqual(resultado["id"], 1)
        self.assertEqual(resultado["jogador_origem"], 1)
        self.assertEqual(resultado["jogador_destino"], 2)
        self.assertEqual(resultado["pokemon_oferecido"], "Pikachu")
        self.assertEqual(resultado["pokemon_desejado"], "Staryu")
        self.assertFalse(resultado["status"])

    # ---- GerenciadorDeTroca ----
    def test_listar_propostas(self):
        gerente = GerenciadorDeTroca(NotificacaoJogador())
        gerente.armazenar_proposta(self.troca)
        resultado = gerente.listar_propostas(self.jogador1)
        self.assertEqual(len(resultado), 1)

    def test_analisar_proposta(self):
        gerente = GerenciadorDeTroca(NotificacaoJogador())
        resultado = gerente.analisar_proposta(self.troca)
        self.assertTrue(resultado)
        self.assertTrue(self.troca.status)

if __name__ == '__main__':
    unittest.main()