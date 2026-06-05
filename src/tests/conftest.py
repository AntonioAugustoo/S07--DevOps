import os
import pytest
from unittest.mock import patch, MagicMock
from app.models.jogador import Jogador
from app.models.pokemon import Pokemon
from app.models.troca import Troca
from app.services.gerenciador_troca import GerenciadorDeTroca
from app.notifications.notificacao_jogador import NotificacaoJogador

# Garante que CWD seja src/ para que caminhos relativos de main.py funcionem
_src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_src_dir)

# Mock do MongoDB antes de main.py ser importado pelos arquivos de teste.
# Sem isso, colecao_propostas.find() no nível de módulo de main.py tentaria
# conectar ao MongoDB real e travaria a coleção de testes.
_mock_collection = MagicMock()
_mock_collection.find.return_value = []
patch("database.colecao_propostas", _mock_collection).start()


@pytest.fixture
def jogador1():
    return Jogador(1, "Ash")


@pytest.fixture
def jogador2():
    return Jogador(2, "Misty")


@pytest.fixture
def pokemon1():
    return Pokemon(1, "Pikachu", "disponivel", 10)


@pytest.fixture
def pokemon2():
    return Pokemon(2, "Staryu", "disponivel", 8)


@pytest.fixture
def troca(jogador1, jogador2, pokemon1, pokemon2):
    return Troca("troca-test-1", jogador1, jogador2, pokemon1, pokemon2)


@pytest.fixture
def gerenciador():
    return GerenciadorDeTroca(NotificacaoJogador())
