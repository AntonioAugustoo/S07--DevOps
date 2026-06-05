import pytest
from unittest.mock import patch, MagicMock

from app.models.jogador import Jogador
from app.models.pokemon import Pokemon
from app.models.troca import Troca
from app.services.gerenciador_troca import GerenciadorDeTroca
from app.notifications.notificacao_jogador import NotificacaoJogador
from app.gerencia_propostas import salvar_proposta_json, atualizar_status_proposta


@pytest.fixture
def jogadores_e_pokemons():
    ash = Jogador(1, "Ash")
    misty = Jogador(2, "Misty")
    pikachu = Pokemon(1, "Pikachu", "disponivel", 10)
    staryu = Pokemon(2, "Staryu", "disponivel", 8)
    ash.pokemons.append(pikachu)
    misty.pokemons.append(staryu)
    return ash, misty, pikachu, staryu


@pytest.fixture
def troca_fixture(jogadores_e_pokemons):
    ash, misty, pikachu, staryu = jogadores_e_pokemons
    return Troca("uuid-001", ash, misty, pikachu, staryu)


@pytest.fixture
def gerenciador():
    return GerenciadorDeTroca(NotificacaoJogador())


class TestSalvarPropostaJson:
    def test_salvar_proposta_nova(self, troca_fixture):
        mock_col = MagicMock()
        with patch("app.gerencia_propostas.colecao_propostas", mock_col):
            salvar_proposta_json(troca_fixture)

        mock_col.insert_one.assert_called_once()
        doc = mock_col.insert_one.call_args[0][0]
        assert doc["id"] == "uuid-001"
        assert doc["pokemon_oferecido"] == "Pikachu" and doc["pokemon_desejado"] == "Staryu"
        assert doc["jogador_origem"] == 1 and doc["jogador_destino"] == 2
        assert doc["ativa"] is True and doc["resposta"] == "pendente"
        assert {"id", "pokemon_oferecido", "pokemon_desejado",
                "jogador_origem", "jogador_destino", "ativa", "resposta"} == set(doc.keys())

    def test_adiciona_a_arquivo_existente(self, troca_fixture):
        outra = Troca(
            "uuid-000",
            Jogador(3, "Brock"), Jogador(4, "Gary"),
            Pokemon(3, "Charmander", "disponivel", 5),
            Pokemon(4, "Bulbasaur", "disponivel", 5),
        )
        mock_col = MagicMock()
        with patch("app.gerencia_propostas.colecao_propostas", mock_col):
            salvar_proposta_json(outra)
            salvar_proposta_json(troca_fixture)

        assert mock_col.insert_one.call_count == 2
        ids = {mock_col.insert_one.call_args_list[i][0][0]["id"] for i in range(2)}
        assert ids == {"uuid-000", "uuid-001"}


class TestAtualizarStatusProposta:
    def test_atualizar_status_aceita(self, jogadores_e_pokemons, gerenciador):
        ash, misty, pikachu, staryu = jogadores_e_pokemons
        troca = Troca("uuid-001", ash, misty, pikachu, staryu)
        misty.propostas_recebidas.append(troca)

        doc_mongo = {
            "id": "uuid-001", "pokemon_oferecido": "Pikachu",
            "pokemon_desejado": "Staryu", "jogador_origem": 1,
            "jogador_destino": 2, "ativa": True, "resposta": "pendente",
        }
        mock_col = MagicMock()
        mock_col.find_one.return_value = doc_mongo
        mock_gerenciador = MagicMock()

        with patch("app.gerencia_propostas.colecao_propostas", mock_col):
            atualizar_status_proposta(
                "uuid-001", "aceita", {1: ash, 2: misty}, {1: pikachu, 2: staryu}, mock_gerenciador
            )

        assert pikachu in misty.pokemons and staryu in ash.pokemons
        assert pikachu not in ash.pokemons and staryu not in misty.pokemons
        assert troca.status is True
        mock_col.update_one.assert_called_once_with(
            {"id": "uuid-001"},
            {"$set": {"resposta": "aceita", "ativa": False}},
        )
        mock_gerenciador.analisar_proposta.assert_called_once()

    def test_atualizar_status_erros(self, gerenciador):
        mock_col = MagicMock()
        mock_col.find_one.return_value = None

        with patch("app.gerencia_propostas.colecao_propostas", mock_col):
            with pytest.raises(Exception, match="Proposta não encontrada."):
                atualizar_status_proposta("uuid-001", "aceita", {}, {}, gerenciador)

        ash = Jogador(1, "Ash")
        misty = Jogador(2, "Misty")
        doc_invalido = {
            "id": "uuid-001", "pokemon_oferecido": "Fake",
            "pokemon_desejado": "Outro", "jogador_origem": 1,
            "jogador_destino": 2, "ativa": True, "resposta": "pendente",
        }
        mock_col.find_one.return_value = doc_invalido
        with patch("app.gerencia_propostas.colecao_propostas", mock_col):
            with pytest.raises(Exception, match="Dados inválidos para processar troca."):
                atualizar_status_proposta("uuid-001", "aceita", {1: ash, 2: misty}, {}, gerenciador)
