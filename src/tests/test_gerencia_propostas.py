import json
import pytest

from app.models.jogador import Jogador
from app.models.pokemon import Pokemon
from app.models.troca import Troca
from app.services.gerenciador_troca import GerenciadorDeTroca
from app.notifications.notificacao_jogador import NotificacaoJogador
from app.gerencia_propostas import salvar_proposta_json, atualizar_status_proposta


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# salvar_proposta_json
# ---------------------------------------------------------------------------

class TestSalvarPropostaJson:
    def test_cria_arquivo_quando_nao_existe(self, troca_fixture, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        salvar_proposta_json(troca_fixture)

        arquivo = tmp_path / "propostas_troca.json"
        assert arquivo.exists()
        conteudo = json.loads(arquivo.read_text())
        assert len(conteudo) == 1

    def test_proposta_salva_com_id_correto(self, troca_fixture, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        salvar_proposta_json(troca_fixture)

        conteudo = json.loads((tmp_path / "propostas_troca.json").read_text())
        assert conteudo[0]["id"] == "uuid-001"

    def test_proposta_salva_com_nomes_corretos(self, troca_fixture, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        salvar_proposta_json(troca_fixture)

        conteudo = json.loads((tmp_path / "propostas_troca.json").read_text())
        p = conteudo[0]
        assert p["pokemon_oferecido"] == "Pikachu"
        assert p["pokemon_desejado"] == "Staryu"

    def test_proposta_salva_com_ids_jogadores(self, troca_fixture, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        salvar_proposta_json(troca_fixture)

        conteudo = json.loads((tmp_path / "propostas_troca.json").read_text())
        p = conteudo[0]
        assert p["jogador_origem"] == 1
        assert p["jogador_destino"] == 2

    def test_proposta_salva_como_ativa_e_pendente(self, troca_fixture, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        salvar_proposta_json(troca_fixture)

        conteudo = json.loads((tmp_path / "propostas_troca.json").read_text())
        p = conteudo[0]
        assert p["ativa"] is True
        assert p["resposta"] == "pendente"

    def test_adiciona_a_arquivo_existente(self, troca_fixture, tmp_path, monkeypatch):
        _proposta_no_arquivo(tmp_path, [{
            "id": "uuid-000",
            "pokemon_oferecido": "Charmander",
            "pokemon_desejado": "Bulbasaur",
            "jogador_origem": 3,
            "jogador_destino": 4,
            "ativa": True,
            "resposta": "pendente",
        }])
        monkeypatch.chdir(tmp_path)

        salvar_proposta_json(troca_fixture)

        conteudo = json.loads((tmp_path / "propostas_troca.json").read_text())
        assert len(conteudo) == 2
        ids = [p["id"] for p in conteudo]
        assert "uuid-000" in ids
        assert "uuid-001" in ids

    def test_json_valido_apos_salvar(self, troca_fixture, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        salvar_proposta_json(troca_fixture)

        # Não deve lançar exceção
        json.loads((tmp_path / "propostas_troca.json").read_text())

    def test_estrutura_completa_dos_campos(self, troca_fixture, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        salvar_proposta_json(troca_fixture)

        p = json.loads((tmp_path / "propostas_troca.json").read_text())[0]
        campos_esperados = {"id", "pokemon_oferecido", "pokemon_desejado",
                            "jogador_origem", "jogador_destino", "ativa", "resposta"}
        assert campos_esperados == set(p.keys())


# ---------------------------------------------------------------------------
# atualizar_status_proposta
# ---------------------------------------------------------------------------

class TestAtualizarStatusProposta:
    def test_troca_pokemon_entre_jogadores(self, jogadores_e_pokemons, tmp_path, monkeypatch, gerenciador):
        ash, misty, pikachu, staryu = jogadores_e_pokemons
        _proposta_no_arquivo(tmp_path, [{
            "id": "uuid-001",
            "pokemon_oferecido": "Pikachu",
            "pokemon_desejado": "Staryu",
            "jogador_origem": 1,
            "jogador_destino": 2,
            "ativa": True,
            "resposta": "pendente",
        }])
        monkeypatch.chdir(tmp_path)

        atualizar_status_proposta("uuid-001", "aceita",
                                  {1: ash, 2: misty}, {1: pikachu, 2: staryu}, gerenciador)

        assert pikachu in misty.pokemons
        assert staryu in ash.pokemons
        assert pikachu not in ash.pokemons
        assert staryu not in misty.pokemons

    def test_arquivo_atualizado_com_status_aceita(self, jogadores_e_pokemons, tmp_path, monkeypatch, gerenciador):
        ash, misty, pikachu, staryu = jogadores_e_pokemons
        arquivo = _proposta_no_arquivo(tmp_path, [{
            "id": "uuid-001",
            "pokemon_oferecido": "Pikachu",
            "pokemon_desejado": "Staryu",
            "jogador_origem": 1,
            "jogador_destino": 2,
            "ativa": True,
            "resposta": "pendente",
        }])
        monkeypatch.chdir(tmp_path)

        atualizar_status_proposta("uuid-001", "aceita",
                                  {1: ash, 2: misty}, {1: pikachu, 2: staryu}, gerenciador)

        conteudo = json.loads(arquivo.read_text())
        assert conteudo[0]["resposta"] == "aceita"
        assert conteudo[0]["ativa"] is False

    def test_arquivo_atualizado_com_status_recusada(self, jogadores_e_pokemons, tmp_path, monkeypatch, gerenciador):
        ash, misty, pikachu, staryu = jogadores_e_pokemons
        arquivo = _proposta_no_arquivo(tmp_path, [{
            "id": "uuid-001",
            "pokemon_oferecido": "Pikachu",
            "pokemon_desejado": "Staryu",
            "jogador_origem": 1,
            "jogador_destino": 2,
            "ativa": True,
            "resposta": "pendente",
        }])
        monkeypatch.chdir(tmp_path)

        atualizar_status_proposta("uuid-001", "recusada",
                                  {1: ash, 2: misty}, {1: pikachu, 2: staryu}, gerenciador)

        conteudo = json.loads(arquivo.read_text())
        assert conteudo[0]["resposta"] == "recusada"

    def test_status_troca_atualizado_em_memoria(self, jogadores_e_pokemons, tmp_path, monkeypatch, gerenciador):
        ash, misty, pikachu, staryu = jogadores_e_pokemons
        troca = Troca("uuid-001", ash, misty, pikachu, staryu)
        misty.propostas_recebidas.append(troca)

        _proposta_no_arquivo(tmp_path, [{
            "id": "uuid-001",
            "pokemon_oferecido": "Pikachu",
            "pokemon_desejado": "Staryu",
            "jogador_origem": 1,
            "jogador_destino": 2,
            "ativa": True,
            "resposta": "pendente",
        }])
        monkeypatch.chdir(tmp_path)

        atualizar_status_proposta("uuid-001", "aceita",
                                  {1: ash, 2: misty}, {1: pikachu, 2: staryu}, gerenciador)

        assert troca.status is True

    def test_gerenciador_analisa_proposta(self, jogadores_e_pokemons, tmp_path, monkeypatch):
        from unittest.mock import MagicMock
        ash, misty, pikachu, staryu = jogadores_e_pokemons
        _proposta_no_arquivo(tmp_path, [{
            "id": "uuid-001",
            "pokemon_oferecido": "Pikachu",
            "pokemon_desejado": "Staryu",
            "jogador_origem": 1,
            "jogador_destino": 2,
            "ativa": True,
            "resposta": "pendente",
        }])
        monkeypatch.chdir(tmp_path)

        mock_gerenciador = MagicMock()
        atualizar_status_proposta("uuid-001", "aceita",
                                  {1: ash, 2: misty}, {1: pikachu, 2: staryu}, mock_gerenciador)

        mock_gerenciador.analisar_proposta.assert_called_once()

    def test_proposta_nao_encontrada_levanta_excecao(self, tmp_path, monkeypatch, gerenciador):
        _proposta_no_arquivo(tmp_path, [])
        monkeypatch.chdir(tmp_path)

        with pytest.raises(Exception, match="Proposta não encontrada."):
            atualizar_status_proposta("id-inexistente", "aceita", {}, {}, gerenciador)

    def test_arquivo_nao_encontrado_levanta_excecao(self, tmp_path, monkeypatch, gerenciador):
        monkeypatch.chdir(tmp_path)  # tmp_path sem arquivo propostas_troca.json

        with pytest.raises(Exception, match="Arquivo de propostas não encontrado."):
            atualizar_status_proposta("uuid-001", "aceita", {}, {}, gerenciador)

    def test_dados_invalidos_levanta_excecao(self, tmp_path, monkeypatch, gerenciador):
        ash = Jogador(1, "Ash")
        misty = Jogador(2, "Misty")
        # Sem pokémons nos jogadores → pokemon_oferecido e pokemon_desejado serão None
        _proposta_no_arquivo(tmp_path, [{
            "id": "uuid-001",
            "pokemon_oferecido": "PokemonInexistente",
            "pokemon_desejado": "OutroPokemon",
            "jogador_origem": 1,
            "jogador_destino": 2,
            "ativa": True,
            "resposta": "pendente",
        }])
        monkeypatch.chdir(tmp_path)

        with pytest.raises(Exception, match="Dados inválidos para processar troca."):
            atualizar_status_proposta("uuid-001", "aceita",
                                      {1: ash, 2: misty}, {}, gerenciador)

    def test_json_valido_apos_atualizar(self, jogadores_e_pokemons, tmp_path, monkeypatch, gerenciador):
        ash, misty, pikachu, staryu = jogadores_e_pokemons
        arquivo = _proposta_no_arquivo(tmp_path, [{
            "id": "uuid-001",
            "pokemon_oferecido": "Pikachu",
            "pokemon_desejado": "Staryu",
            "jogador_origem": 1,
            "jogador_destino": 2,
            "ativa": True,
            "resposta": "pendente",
        }])
        monkeypatch.chdir(tmp_path)

        atualizar_status_proposta("uuid-001", "aceita",
                                  {1: ash, 2: misty}, {1: pikachu, 2: staryu}, gerenciador)

        # Não deve lançar exceção (validação de JSON bem formado)
        json.loads(arquivo.read_text())
