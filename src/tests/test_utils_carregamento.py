import json
import pytest

from app.models.jogador import Jogador
from app.models.pokemon import Pokemon
from app.services.gerenciador_troca import GerenciadorDeTroca
from app.notifications.notificacao_jogador import NotificacaoJogador
from app.utils_carregamento import carregar_dados_do_json, carregar_propostas_json


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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
def arquivo_propostas(tmp_path):
    dados = [{
        "id": "prop-001",
        "pokemon_oferecido": "Pikachu",
        "pokemon_desejado": "Staryu",
        "jogador_origem": 1,
        "jogador_destino": 2,
        "ativa": True,
    }]
    arquivo = tmp_path / "propostas_test.json"
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


# ---------------------------------------------------------------------------
# carregar_dados_do_json
# ---------------------------------------------------------------------------

class TestCarregarDadosDoJson:
    def test_carrega_dois_jogadores(self, arquivo_jogadores):
        jogadores, _ = carregar_dados_do_json(arquivo_jogadores)
        assert len(jogadores) == 2

    def test_jogadores_com_ids_corretos(self, arquivo_jogadores):
        jogadores, _ = carregar_dados_do_json(arquivo_jogadores)
        assert 1 in jogadores
        assert 2 in jogadores

    def test_jogadores_com_nomes_corretos(self, arquivo_jogadores):
        jogadores, _ = carregar_dados_do_json(arquivo_jogadores)
        assert jogadores[1].nome == "Ash"
        assert jogadores[2].nome == "Misty"

    def test_carrega_tres_pokemons(self, arquivo_jogadores):
        _, pokemons = carregar_dados_do_json(arquivo_jogadores)
        assert len(pokemons) == 3

    def test_pokemon_com_atributos_corretos(self, arquivo_jogadores):
        _, pokemons = carregar_dados_do_json(arquivo_jogadores)
        p = pokemons[1]
        assert p.nome == "Pikachu"
        assert p.nivel == 10
        assert p.status == "disponivel"

    def test_pokemon_status_ocupado_preservado(self, arquivo_jogadores):
        _, pokemons = carregar_dados_do_json(arquivo_jogadores)
        assert pokemons[3].status == "ocupado"

    def test_pikachu_associado_ao_ash(self, arquivo_jogadores):
        jogadores, _ = carregar_dados_do_json(arquivo_jogadores)
        nomes = [p.nome for p in jogadores[1].pokemons]
        assert "Pikachu" in nomes

    def test_misty_tem_dois_pokemons(self, arquivo_jogadores):
        jogadores, _ = carregar_dados_do_json(arquivo_jogadores)
        assert len(jogadores[2].pokemons) == 2

    def test_misty_tem_staryu_e_psyduck(self, arquivo_jogadores):
        jogadores, _ = carregar_dados_do_json(arquivo_jogadores)
        nomes = [p.nome for p in jogadores[2].pokemons]
        assert "Staryu" in nomes
        assert "Psyduck" in nomes

    def test_pokemon_sem_dono_valido_nao_associado_a_jogador(self, tmp_path):
        dados = {
            "jogadores": [{"id": 1, "nome": "Ash"}],
            "pokemons": [
                {"id": 99, "nome": "Mew", "status": "disponivel", "nivel": 50, "dono_id": 999},
            ],
        }
        arquivo = str(tmp_path / "test.json")
        (tmp_path / "test.json").write_text(json.dumps(dados))

        jogadores, pokemons = carregar_dados_do_json(arquivo)
        assert len(jogadores[1].pokemons) == 0
        assert 99 in pokemons

    def test_retorna_tupla_com_dois_dicionarios(self, arquivo_jogadores):
        resultado = carregar_dados_do_json(arquivo_jogadores)
        assert isinstance(resultado, tuple)
        assert len(resultado) == 2
        assert isinstance(resultado[0], dict)
        assert isinstance(resultado[1], dict)

    def test_jogador_instancia_correta(self, arquivo_jogadores):
        jogadores, _ = carregar_dados_do_json(arquivo_jogadores)
        assert isinstance(jogadores[1], Jogador)

    def test_pokemon_instancia_correta(self, arquivo_jogadores):
        _, pokemons = carregar_dados_do_json(arquivo_jogadores)
        assert isinstance(pokemons[1], Pokemon)


# ---------------------------------------------------------------------------
# carregar_propostas_json
# ---------------------------------------------------------------------------

class TestCarregarPropostasJson:
    def test_carrega_uma_proposta(self, arquivo_propostas, jogadores_pokemons_para_proposta):
        jogadores, pokemons = jogadores_pokemons_para_proposta
        gerenciador = GerenciadorDeTroca(NotificacaoJogador())

        carregar_propostas_json(arquivo_propostas, jogadores, pokemons, gerenciador)

        assert len(gerenciador.propostas) == 1

    def test_proposta_com_id_correto(self, arquivo_propostas, jogadores_pokemons_para_proposta):
        jogadores, pokemons = jogadores_pokemons_para_proposta
        gerenciador = GerenciadorDeTroca(NotificacaoJogador())

        carregar_propostas_json(arquivo_propostas, jogadores, pokemons, gerenciador)

        assert gerenciador.propostas[0].id == "prop-001"

    def test_proposta_com_jogadores_corretos(self, arquivo_propostas, jogadores_pokemons_para_proposta):
        jogadores, pokemons = jogadores_pokemons_para_proposta
        gerenciador = GerenciadorDeTroca(NotificacaoJogador())

        carregar_propostas_json(arquivo_propostas, jogadores, pokemons, gerenciador)

        proposta = gerenciador.propostas[0]
        assert proposta.jogador_origem.id == 1
        assert proposta.jogador_destino.id == 2

    def test_proposta_com_pokemons_corretos(self, arquivo_propostas, jogadores_pokemons_para_proposta):
        jogadores, pokemons = jogadores_pokemons_para_proposta
        gerenciador = GerenciadorDeTroca(NotificacaoJogador())

        carregar_propostas_json(arquivo_propostas, jogadores, pokemons, gerenciador)

        proposta = gerenciador.propostas[0]
        assert proposta.pokemon_oferecido.nome == "Pikachu"
        assert proposta.pokemon_desejado.nome == "Staryu"

    def test_arquivo_inexistente_nao_levanta_excecao(self):
        gerenciador = GerenciadorDeTroca(NotificacaoJogador())
        carregar_propostas_json("arquivo_que_nao_existe.json", {}, {}, gerenciador)
        assert len(gerenciador.propostas) == 0

    def test_arquivo_vazio_nao_adiciona_propostas(self, tmp_path):
        arquivo = str(tmp_path / "vazio.json")
        (tmp_path / "vazio.json").write_text("[]")
        gerenciador = GerenciadorDeTroca(NotificacaoJogador())

        carregar_propostas_json(arquivo, {}, {}, gerenciador)

        assert len(gerenciador.propostas) == 0

    def test_proposta_com_pokemon_inexistente_ignorada(self, tmp_path):
        dados = [{
            "id": "prop-bad",
            "pokemon_oferecido": "PokemonFake",
            "pokemon_desejado": "OutroFake",
            "jogador_origem": 1,
            "jogador_destino": 2,
            "ativa": True,
        }]
        arquivo = str(tmp_path / "propostas.json")
        (tmp_path / "propostas.json").write_text(json.dumps(dados))

        ash = Jogador(1, "Ash")
        misty = Jogador(2, "Misty")
        gerenciador = GerenciadorDeTroca(NotificacaoJogador())

        carregar_propostas_json(arquivo, {1: ash, 2: misty}, {}, gerenciador)

        assert len(gerenciador.propostas) == 0

    def test_proposta_com_jogador_inexistente_ignorada(self, tmp_path):
        pikachu = Pokemon(1, "Pikachu", "disponivel", 10)
        staryu = Pokemon(2, "Staryu", "disponivel", 8)
        dados = [{
            "id": "prop-bad",
            "pokemon_oferecido": "Pikachu",
            "pokemon_desejado": "Staryu",
            "jogador_origem": 99,  # não existe
            "jogador_destino": 2,
            "ativa": True,
        }]
        arquivo = str(tmp_path / "propostas.json")
        (tmp_path / "propostas.json").write_text(json.dumps(dados))

        misty = Jogador(2, "Misty")
        gerenciador = GerenciadorDeTroca(NotificacaoJogador())

        carregar_propostas_json(arquivo, {2: misty}, {1: pikachu, 2: staryu}, gerenciador)

        assert len(gerenciador.propostas) == 0

    def test_multiplas_propostas_validas_carregadas(self, tmp_path):
        ash = Jogador(1, "Ash")
        misty = Jogador(2, "Misty")
        brock = Jogador(3, "Brock")
        p1 = Pokemon(1, "Pikachu", "disponivel", 10)
        p2 = Pokemon(2, "Staryu", "disponivel", 8)
        p3 = Pokemon(3, "Geodude", "disponivel", 12)
        ash.pokemons.extend([p1, p3])
        misty.pokemons.append(p2)
        brock.pokemons.append(p3)

        dados = [
            {"id": "p1", "pokemon_oferecido": "Pikachu", "pokemon_desejado": "Staryu",
             "jogador_origem": 1, "jogador_destino": 2, "ativa": True},
            {"id": "p2", "pokemon_oferecido": "Geodude", "pokemon_desejado": "Pikachu",
             "jogador_origem": 3, "jogador_destino": 1, "ativa": True},
        ]
        arquivo = str(tmp_path / "multi.json")
        (tmp_path / "multi.json").write_text(json.dumps(dados))

        gerenciador = GerenciadorDeTroca(NotificacaoJogador())
        carregar_propostas_json(arquivo, {1: ash, 2: misty, 3: brock},
                                {1: p1, 2: p2, 3: p3}, gerenciador)

        assert len(gerenciador.propostas) == 2
