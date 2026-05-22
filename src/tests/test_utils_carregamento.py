import json
import pytest

from app.models.jogador import Jogador
from app.models.pokemon import Pokemon
from app.services.gerenciador_troca import GerenciadorDeTroca
from app.notifications.notificacao_jogador import NotificacaoJogador
from app.utils_carregamento import carregar_dados_do_json, carregar_propostas_json


@pytest.fixture
def arquivo_jogadores(tmp_path):
    dados = {
        "jogadores": [
            {"id": 1, "nome": "Ash"},
            {"id": 2, "nome": "Misty"},
        ],
        "pokemons": [
            {"id": 1, "nome": "Pikachu", "status": "disponivel", "nivel": 10, "dono_id": 1},
            {"id": 2, "nome": "Staryu", "status": "disponivel", "nivel": 8, "dono_id": 2},
            {"id": 3, "nome": "Psyduck", "status": "ocupado", "nivel": 7, "dono_id": 2},
        ],
    }
    arquivo = tmp_path / "jogadores_test.json"
    arquivo.write_text(json.dumps(dados))
    return str(arquivo)


@pytest.fixture
def jogadores_pokemons_para_proposta():
    ash = Jogador(1, "Ash")
    misty = Jogador(2, "Misty")
    pikachu = Pokemon(1, "Pikachu", "disponivel", 10)
    staryu = Pokemon(2, "Staryu", "disponivel", 8)
    ash.pokemons.append(pikachu)
    misty.pokemons.append(staryu)
    return {1: ash, 2: misty}, {1: pikachu, 2: staryu}


class TestCarregarDadosDoJson:
    def test_carrega_jogadores_e_pokemons(self, arquivo_jogadores):
        jogadores, pokemons = carregar_dados_do_json(arquivo_jogadores)

        assert isinstance(jogadores, dict) and isinstance(pokemons, dict)
        assert isinstance(jogadores[1], Jogador) and isinstance(pokemons[1], Pokemon)
        assert len(jogadores) == 2 and len(pokemons) == 3
        assert jogadores[1].nome == "Ash" and jogadores[2].nome == "Misty"
        assert pokemons[1].nome == "Pikachu" and pokemons[1].nivel == 10
        assert pokemons[3].status == "ocupado"
        assert any(p.nome == "Pikachu" for p in jogadores[1].pokemons)
        assert len(jogadores[2].pokemons) == 2

    def test_pokemon_sem_dono_valido_nao_associado(self, tmp_path):
        dados = {
            "jogadores": [{"id": 1, "nome": "Ash"}],
            "pokemons": [{"id": 99, "nome": "Mew", "status": "disponivel", "nivel": 50, "dono_id": 999}],
        }
        arquivo = str(tmp_path / "test.json")
        (tmp_path / "test.json").write_text(json.dumps(dados))

        jogadores, pokemons = carregar_dados_do_json(arquivo)
        assert len(jogadores[1].pokemons) == 0
        assert 99 in pokemons

    def test_proposta_carregada_corretamente(self, tmp_path, jogadores_pokemons_para_proposta):
        dados = [{"id": "prop-001", "pokemon_oferecido": "Pikachu", "pokemon_desejado": "Staryu",
                  "jogador_origem": 1, "jogador_destino": 2, "ativa": True}]
        arquivo = str(tmp_path / "propostas.json")
        (tmp_path / "propostas.json").write_text(json.dumps(dados))

        jogadores, pokemons = jogadores_pokemons_para_proposta
        gerenciador = GerenciadorDeTroca(NotificacaoJogador())
        carregar_propostas_json(arquivo, jogadores, pokemons, gerenciador)

        assert len(gerenciador.propostas) == 1
        p = gerenciador.propostas[0]
        assert p.id == "prop-001"
        assert p.jogador_origem.id == 1 and p.jogador_destino.id == 2
        assert p.pokemon_oferecido.nome == "Pikachu" and p.pokemon_desejado.nome == "Staryu"

    def test_proposta_invalida_ignorada(self, tmp_path):
        gerenciador = GerenciadorDeTroca(NotificacaoJogador())

        # arquivo inexistente não levanta exceção
        carregar_propostas_json("nao_existe.json", {}, {}, gerenciador)
        assert len(gerenciador.propostas) == 0

        # proposta com pokemon inexistente é ignorada
        dados = [{"id": "bad", "pokemon_oferecido": "Fake", "pokemon_desejado": "Outro",
                  "jogador_origem": 1, "jogador_destino": 2, "ativa": True}]
        arquivo = str(tmp_path / "p.json")
        (tmp_path / "p.json").write_text(json.dumps(dados))
        ash = Jogador(1, "Ash")
        misty = Jogador(2, "Misty")
        carregar_propostas_json(arquivo, {1: ash, 2: misty}, {}, gerenciador)
        assert len(gerenciador.propostas) == 0
