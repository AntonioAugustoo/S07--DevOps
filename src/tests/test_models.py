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

class TestePokemonSubclasses(unittest.TestCase):
    def test_pokemon_shiny_brilhar(self):
        shiny = PokemonShiny(3, "Charizard", "disponivel", 15)
        self.assertEqual(shiny.brilhar(), "Charizard está brilhando!")

    def test_pokemon_mega_evoluir(self):
        mega = PokemonMega(4, "Blaziken", "disponivel", 20)
        self.assertEqual(mega.mega_evoluir(), "Blaziken mega evoluiu!")

    def test_pokemon_atacar(self):
        p = Pokemon(5, "Bulbasaur", "disponivel", 5)
        self.assertEqual(p.atacar(), "Bulbasaur atacou!")

    def test_pokemon_shiny_herda_atributos(self):
        shiny = PokemonShiny(6, "Gengar", "disponivel", 12)
        self.assertEqual(shiny.id, 6)
        self.assertEqual(shiny.nome, "Gengar")
        self.assertEqual(shiny.status, "disponivel")
        self.assertEqual(shiny.nivel, 12)

    def test_pokemon_mega_herda_atributos(self):
        mega = PokemonMega(7, "Mewtwo", "ocupado", 50)
        self.assertEqual(mega.id, 7)
        self.assertEqual(mega.nome, "Mewtwo")
        self.assertEqual(mega.status, "ocupado")


class TesteNotificacaoFactory(unittest.TestCase):
    def test_criar_notificacao_retorna_instancia(self):
        factory = NotificacaoFactory()
        notificacao = factory.criar_notificacao()
        self.assertIsNotNone(notificacao)
        self.assertIsInstance(notificacao, NotificacaoJogador)


class TesteINotificacaoAbstrata(unittest.TestCase):
    def test_metodo_abstrato_executavel_via_super(self):
        class ConcreteNotif(INotificacao):
            def notificar(self, jogador, mensagem: str):
                return super().notificar(jogador, mensagem)

        jogador = Jogador(1, "Ash")
        notif = ConcreteNotif()
        resultado = notif.notificar(jogador, "teste")
        self.assertIsNone(resultado)

    def test_nao_e_possivel_instanciar_diretamente(self):
        with self.assertRaises(TypeError):
            INotificacao()


class TesteNotificacaoNovoPokemon(unittest.TestCase):
    def test_instanciacao_falha_sem_notificar_implementado(self):
        with self.assertRaises(TypeError):
            NotificacaoNovoPokemon()

    def test_notificar_novo_pokemon_via_subclasse(self):
        class NovoPokemonConcreto(NotificacaoNovoPokemon):
            def notificar(self, jogador, mensagem: str):
                pass

        p = Pokemon(1, "Pikachu", "disponivel", 10)
        notif = NovoPokemonConcreto()
        notif.notificar_novo_pokemon(p, "encontrado!")


if __name__ == '__main__':
    unittest.main()