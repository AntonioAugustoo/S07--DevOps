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

    def test_envio_proposta_e_notificacao(self):
        mock_notificacao = MagicMock()
        gerente = GerenciadorDeTroca(mock_notificacao)
        gerente.enviar_proposta(self.troca)
        mock_notificacao.notificar.assert_called_once_with(self.jogador2, "Nova proposta de troca enviada!")

        real = NotificacaoJogador()
        decorado = NotificacaoDecorator(real)
        self.assertIsNone(decorado.notificar(self.jogador1, "Mensagem de teste"))

        mock_notif = MagicMock()
        NotificacaoDecorator(mock_notif).notificar(self.jogador1, "msg")
        mock_notif.notificar.assert_called_once_with(self.jogador1, "msg")

    def test_validadores(self):
        # chain completa passa
        self.assertTrue(ValidadorNivel(ValidadorStatus()).validar(self.troca))

        # status ocupado falha
        self.pokemon1.status = "ocupado"
        self.assertFalse(ValidadorStatus().validar(self.troca))
        self.assertFalse(ValidadorStatus(ValidadorNivel()).validar(self.troca))
        self.pokemon1.status = "disponivel"

        # nível insuficiente falha
        fraco = Pokemon(3, "Pidgey", "disponivel", 2)
        forte = Pokemon(4, "Dragonite", "disponivel", 50)
        self.assertFalse(ValidadorNivel().validar(Troca(2, self.jogador1, self.jogador2, fraco, forte)))

        # nível igual passa
        p1 = Pokemon(5, "A", "disponivel", 10)
        p2 = Pokemon(6, "B", "disponivel", 10)
        self.assertTrue(ValidadorNivel().validar(Troca(3, self.jogador1, self.jogador2, p1, p2)))

        # ValidadorBase delega ao próximo
        mock_proximo = MagicMock()
        mock_proximo.validar.return_value = False
        self.assertFalse(ValidadorBase(mock_proximo).validar(self.troca))

    def test_gerenciador_listar_propostas(self):
        gerente = GerenciadorDeTroca(NotificacaoJogador())
        gerente.armazenar_proposta(self.troca)
        self.assertEqual(len(gerente.listar_propostas(self.jogador1)), 1)
        self.assertEqual(len(gerente.listar_propostas(self.jogador2)), 1)
        self.assertEqual(gerente.listar_propostas(Jogador(99, "Giovanni")), [])


if __name__ == '__main__':
    unittest.main()
