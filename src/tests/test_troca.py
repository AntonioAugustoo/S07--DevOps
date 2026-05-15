
import unittest
from unittest.mock import MagicMock
from app.models.jogador import Jogador
from app.models.pokemon import Pokemon
from app.models.troca import Troca
from app.services.gerenciador_troca import GerenciadorDeTroca
from app.notifications.notificacao_jogador import NotificacaoJogador
from app.notifications.notificacao_decorator import NotificacaoDecorator
from app.services.validadores import ValidadorNivel, ValidadorStatus

class TesteSistemaTroca(unittest.TestCase):
    def setUp(self):
        self.jogador1 = Jogador(1, "Ash")
        self.jogador2 = Jogador(2, "Misty")
        self.pokemon1 = Pokemon(1, "Pikachu", "disponivel", 10)
        self.pokemon2 = Pokemon(2, "Staryu", "disponivel", 8)
        self.troca = Troca(1, self.pokemon1, self.pokemon2, self.jogador1, self.jogador2)

    def test_envio_proposta_com_mock(self):
        mock_notificacao = MagicMock()
        gerente = GerenciadorDeTroca(mock_notificacao)
        gerente.enviar_proposta(self.troca)
        mock_notificacao.notificar.assert_called_once_with(self.jogador2, "Nova proposta de troca enviada!")

    def test_notificacao_com_decorator(self):
        real = NotificacaoJogador()
        decorado = NotificacaoDecorator(real)
        resultado = decorado.notificar(self.jogador1, "Mensagem de teste")
        self.assertIsNone(resultado)  # Apenas printa log

    def test_chain_of_responsibility(self):
        validador = ValidadorNivel(ValidadorStatus())
        resultado = validador.validar(self.troca)
        self.assertTrue(resultado)

    def test_validacao_falha_status(self):
        self.pokemon1.status = "ocupado"
        validador = ValidadorStatus()
        resultado = validador.validar(self.troca)
        self.assertFalse(resultado)

if __name__ == '__main__':
    unittest.main()
