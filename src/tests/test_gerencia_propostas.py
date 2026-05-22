import json
import pytest

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


def _proposta_no_arquivo(tmp_path, propostas):
    arquivo = tmp_path / "propostas_troca.json"
    arquivo.write_text(json.dumps(propostas))
    return arquivo


class TestSalvarPropostaJson:
    def test_salvar_proposta_nova(self, troca_fixture, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        salvar_proposta_json(troca_fixture)

        arquivo = tmp_path / "propostas_troca.json"
        assert arquivo.exists()
        conteudo = json.loads(arquivo.read_text())
        p = conteudo[0]
        assert p["id"] == "uuid-001"
        assert p["pokemon_oferecido"] == "Pikachu" and p["pokemon_desejado"] == "Staryu"
        assert p["jogador_origem"] == 1 and p["jogador_destino"] == 2
        assert p["ativa"] is True and p["resposta"] == "pendente"
        assert {"id", "pokemon_oferecido", "pokemon_desejado",
                "jogador_origem", "jogador_destino", "ativa", "resposta"} == set(p.keys())

    def test_adiciona_a_arquivo_existente(self, troca_fixture, tmp_path, monkeypatch):
        _proposta_no_arquivo(tmp_path, [{"id": "uuid-000", "pokemon_oferecido": "Charmander",
                                         "pokemon_desejado": "Bulbasaur", "jogador_origem": 3,
                                         "jogador_destino": 4, "ativa": True, "resposta": "pendente"}])
        monkeypatch.chdir(tmp_path)
        salvar_proposta_json(troca_fixture)

        conteudo = json.loads((tmp_path / "propostas_troca.json").read_text())
        assert len(conteudo) == 2
        assert {p["id"] for p in conteudo} == {"uuid-000", "uuid-001"}


class TestAtualizarStatusProposta:
    def test_atualizar_status_aceita(self, jogadores_e_pokemons, tmp_path, monkeypatch, gerenciador):
        from unittest.mock import MagicMock
        ash, misty, pikachu, staryu = jogadores_e_pokemons
        troca = Troca("uuid-001", ash, misty, pikachu, staryu)
        misty.propostas_recebidas.append(troca)
        arquivo = _proposta_no_arquivo(tmp_path, [{"id": "uuid-001", "pokemon_oferecido": "Pikachu",
                                                    "pokemon_desejado": "Staryu", "jogador_origem": 1,
                                                    "jogador_destino": 2, "ativa": True, "resposta": "pendente"}])
        monkeypatch.chdir(tmp_path)

        mock_gerenciador = MagicMock()
        atualizar_status_proposta("uuid-001", "aceita", {1: ash, 2: misty}, {1: pikachu, 2: staryu}, mock_gerenciador)

        assert pikachu in misty.pokemons and staryu in ash.pokemons
        assert pikachu not in ash.pokemons and staryu not in misty.pokemons
        assert troca.status is True
        conteudo = json.loads(arquivo.read_text())
        assert conteudo[0]["resposta"] == "aceita" and conteudo[0]["ativa"] is False
        mock_gerenciador.analisar_proposta.assert_called_once()

    def test_atualizar_status_erros(self, tmp_path, monkeypatch, gerenciador):
        monkeypatch.chdir(tmp_path)

        with pytest.raises(Exception, match="Arquivo de propostas não encontrado."):
            atualizar_status_proposta("uuid-001", "aceita", {}, {}, gerenciador)

        _proposta_no_arquivo(tmp_path, [])
        with pytest.raises(Exception, match="Proposta não encontrada."):
            atualizar_status_proposta("id-inexistente", "aceita", {}, {}, gerenciador)

        ash = Jogador(1, "Ash")
        misty = Jogador(2, "Misty")
        _proposta_no_arquivo(tmp_path, [{"id": "uuid-001", "pokemon_oferecido": "Fake",
                                         "pokemon_desejado": "Outro", "jogador_origem": 1,
                                         "jogador_destino": 2, "ativa": True, "resposta": "pendente"}])
        with pytest.raises(Exception, match="Dados inválidos para processar troca."):
            atualizar_status_proposta("uuid-001", "aceita", {1: ash, 2: misty}, {}, gerenciador)
