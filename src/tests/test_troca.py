import unittest
from unittest.mock import MagicMock
from app.models.jogador import Jogador
from app.models.pokemon import Pokemon
from app.models.troca import Troca
from app.services.gerenciador_troca import GerenciadorDeTroca
from app.notifications.notificacao_jogador import NotificacaoJogador
from app.notifications.notificacao_decorator import NotificacaoDecorator
from app.services.validadores import ValidadorBase, ValidadorNivel, ValidadorStatus

class TesteSistemaTroca(unittest.TestCase):
    def setUp(self):
        self.jogador1 = Jogador(1, "Ash")
        self.jogador2 = Jogador(2, "Misty")
        self.pokemon1 = Pokemon(1, "Pikachu", "disponivel", 10)
        self.pokemon2 = Pokemon(2, "Staryu", "disponivel", 8)
        self.troca = Troca(1, self.jogador1, self.jogador2, self.pokemon1, self.pokemon2)

    def test_envio_proposta_com_mock(self):
        mock_notificacao = MagicMock()
        gerente = GerenciadorDeTroca(mock_notificacao)
        gerente.enviar_proposta(self.troca)
        mock_notificacao.notificar.assert_called_once_with(self.jogador2, "Nova proposta de troca enviada!")

    def test_notificacao_com_decorator(self):
        real = NotificacaoJogador()
        decorado = NotificacaoDecorator(real)
        resultado = decorado.notificar(self.jogador1, "Mensagem de teste")
        self.assertIsNone(resultado)

    def test_chain_of_responsibility(self):
        validador = ValidadorNivel(ValidadorStatus())
        resultado = validador.validar(self.troca)
        self.assertTrue(resultado)

    def test_validacao_falha_status(self):
        self.pokemon1.status = "ocupado"
        validador = ValidadorStatus()
        resultado = validador.validar(self.troca)
        self.assertFalse(resultado)

    def test_validador_nivel_insuficiente_retorna_false(self):
        fraco = Pokemon(3, "Pidgey", "disponivel", 2)
        forte = Pokemon(4, "Dragonite", "disponivel", 50)
        troca_invalida = Troca(2, self.jogador1, self.jogador2, fraco, forte)
        validador = ValidadorNivel()
        self.assertFalse(validador.validar(troca_invalida))

    def test_validador_nivel_igual_retorna_true(self):
        p1 = Pokemon(3, "A", "disponivel", 10)
        p2 = Pokemon(4, "B", "disponivel", 10)
        troca = Troca(3, self.jogador1, self.jogador2, p1, p2)
        validador = ValidadorNivel()
        self.assertTrue(validador.validar(troca))

    def test_validador_base_sem_proximo_retorna_true(self):
        validador = ValidadorBase()
        self.assertTrue(validador.validar(self.troca))

    def test_validador_base_com_proximo_delega(self):
        mock_proximo = MagicMock()
        mock_proximo.validar.return_value = False
        validador = ValidadorBase(mock_proximo)
        resultado = validador.validar(self.troca)
        self.assertFalse(resultado)
        mock_proximo.validar.assert_called_once_with(self.troca)

    def test_chain_status_falha_antes_de_nivel(self):
        self.pokemon1.status = "ocupado"
        # Status falha → não chega a verificar nível
        validador = ValidadorStatus(ValidadorNivel())
        self.assertFalse(validador.validar(self.troca))

    def test_gerenciador_listar_por_origem_e_destino(self):
        gerente = GerenciadorDeTroca(NotificacaoJogador())
        gerente.armazenar_proposta(self.troca)
        por_origem = gerente.listar_propostas(self.jogador1)
        por_destino = gerente.listar_propostas(self.jogador2)
        self.assertEqual(len(por_origem), 1)
        self.assertEqual(len(por_destino), 1)

    def test_gerenciador_listar_sem_propostas(self):
        jogador_sem_propostas = Jogador(99, "Giovanni")
        gerente = GerenciadorDeTroca(NotificacaoJogador())
        gerente.armazenar_proposta(self.troca)
        resultado = gerente.listar_propostas(jogador_sem_propostas)
        self.assertEqual(resultado, [])

    def test_notificacao_decorator_chama_notificacao_interna(self):
        mock_notif = MagicMock()
        decorado = NotificacaoDecorator(mock_notif)
        decorado.notificar(self.jogador1, "mensagem")
        mock_notif.notificar.assert_called_once_with(self.jogador1, "mensagem")

if __name__ == '__main__':
    unittest.main()