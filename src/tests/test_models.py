import unittest
from app.models.jogador import Jogador
from app.models.pokemon import Pokemon, PokemonShiny, PokemonMega
from app.models.troca import Troca
from app.services.gerenciador_troca import GerenciadorDeTroca
from app.notifications.notificacao_jogador import NotificacaoJogador
from app.notifications.inotificacao import INotificacao
from app.notifications.notificacao_novo_pokemon import NotificacaoNovoPokemon
from app.factory.notificacao_factory import NotificacaoFactory


class TesteModels(unittest.TestCase):

    def setUp(self):
        self.jogador1 = Jogador(1, "Ash")
        self.jogador2 = Jogador(2, "Misty")
        self.pokemon1 = Pokemon(1, "Pikachu", "disponivel", 10)
        self.pokemon2 = Pokemon(2, "Staryu", "disponivel", 8)
        self.troca = Troca(1, self.jogador1, self.jogador2, self.pokemon1, self.pokemon2)

    def test_jogador_to_dict(self):
        resultado_sem_pokemon = self.jogador1.to_dict()
        self.assertEqual(resultado_sem_pokemon["pokemons"], [])

        self.jogador1.pokemons.append(self.pokemon1)
        resultado = self.jogador1.to_dict()
        self.assertEqual(resultado["id"], 1)
        self.assertEqual(resultado["nome"], "Ash")
        self.assertIn("Pikachu", resultado["pokemons"])

    def test_troca_to_dict_e_gerenciador(self):
        resultado = self.troca.to_dict()
        self.assertEqual(resultado["id"], 1)
        self.assertEqual(resultado["pokemon_oferecido"], "Pikachu")
        self.assertFalse(resultado["status"])

        gerente = GerenciadorDeTroca(NotificacaoJogador())
        gerente.armazenar_proposta(self.troca)
        self.assertEqual(len(gerente.listar_propostas(self.jogador1)), 1)
        self.assertTrue(gerente.analisar_proposta(self.troca))

    def test_pokemon_subclasses(self):
        shiny = PokemonShiny(3, "Charizard", "disponivel", 15)
        self.assertEqual(shiny.brilhar(), "Charizard está brilhando!")
        self.assertEqual(shiny.id, 3) and self.assertEqual(shiny.nivel, 15)

        mega = PokemonMega(4, "Blaziken", "disponivel", 20)
        self.assertEqual(mega.mega_evoluir(), "Blaziken mega evoluiu!")
        self.assertEqual(mega.nome, "Blaziken")

        p = Pokemon(5, "Bulbasaur", "disponivel", 5)
        self.assertEqual(p.atacar(), "Bulbasaur atacou!")

    def test_notificacoes(self):
        factory = NotificacaoFactory()
        self.assertIsInstance(factory.criar_notificacao(), NotificacaoJogador)

        with self.assertRaises(TypeError):
            INotificacao()

        with self.assertRaises(TypeError):
            NotificacaoNovoPokemon()

        class NovoPokemonConcreto(NotificacaoNovoPokemon):
            def notificar(self, jogador, mensagem: str):
                pass

        notif = NovoPokemonConcreto()
        notif.notificar_novo_pokemon(self.pokemon1, "encontrado!")


if __name__ == '__main__':
    unittest.main()
