import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.models.jogador import Jogador
from app.models.pokemon import Pokemon
from app.models.troca import Troca
from app.services.gerenciador_troca import GerenciadorDeTroca
from app.notifications.notificacao_jogador import NotificacaoJogador

# conftest.py já ajustou CWD para src/ antes deste módulo ser importado
import main
from main import app


@pytest.fixture(autouse=True)
def mock_mqtt():
    with patch("paho.mqtt.publish.single"):
        yield


@pytest.fixture
def client(monkeypatch):
    ash = Jogador(1, "Ash")
    misty = Jogador(2, "Misty")
    pikachu = Pokemon(1, "Pikachu", "disponivel", 10)
    staryu = Pokemon(2, "Staryu", "disponivel", 8)
    ash.pokemons.append(pikachu)
    misty.pokemons.append(staryu)

    monkeypatch.setattr(main, "jogadores", {1: ash, 2: misty})
    monkeypatch.setattr(main, "pokemons_disponiveis", {1: pikachu, 2: staryu})
    monkeypatch.setattr(main, "gerenciador", GerenciadorDeTroca(NotificacaoJogador()))

    return TestClient(app)


# ---------------------------------------------------------------------------
# POST /proposta
# ---------------------------------------------------------------------------

class TestCriarProposta:
    def test_sucesso_retorna_id_proposta(self, client):
        with patch("main.salvar_proposta_json"):
            resp = client.post("/proposta", json={
                "jogador_origem_id": "1",
                "jogador_destino_id": "2",
                "pokemon_oferecido_id": "1",
                "pokemon_desejado_id": "2",
            })
        assert resp.status_code == 200
        body = resp.json()
        assert "id_proposta" in body
        assert body["mensagem"] == "Proposta criada com sucesso"

    def test_salvar_proposta_chamado_uma_vez(self, client):
        with patch("main.salvar_proposta_json") as mock_save:
            resp = client.post("/proposta", json={
                "jogador_origem_id": "1",
                "jogador_destino_id": "2",
                "pokemon_oferecido_id": "1",
                "pokemon_desejado_id": "2",
            })
        assert resp.status_code == 200
        mock_save.assert_called_once()

    def test_proposta_adicionada_a_lista_destino(self, client, monkeypatch):
        misty = main.jogadores[2]
        with patch("main.salvar_proposta_json"):
            client.post("/proposta", json={
                "jogador_origem_id": "1",
                "jogador_destino_id": "2",
                "pokemon_oferecido_id": "1",
                "pokemon_desejado_id": "2",
            })
        assert len(misty.propostas_recebidas) == 1

    def test_jogador_origem_inexistente_retorna_400(self, client):
        resp = client.post("/proposta", json={
            "jogador_origem_id": "99",
            "jogador_destino_id": "2",
            "pokemon_oferecido_id": "1",
            "pokemon_desejado_id": "2",
        })
        assert resp.status_code == 400

    def test_jogador_destino_inexistente_retorna_400(self, client):
        resp = client.post("/proposta", json={
            "jogador_origem_id": "1",
            "jogador_destino_id": "99",
            "pokemon_oferecido_id": "1",
            "pokemon_desejado_id": "2",
        })
        assert resp.status_code == 400

    def test_pokemon_oferecido_inexistente_retorna_400(self, client):
        resp = client.post("/proposta", json={
            "jogador_origem_id": "1",
            "jogador_destino_id": "2",
            "pokemon_oferecido_id": "99",
            "pokemon_desejado_id": "2",
        })
        assert resp.status_code == 400

    def test_pokemon_desejado_inexistente_retorna_400(self, client):
        resp = client.post("/proposta", json={
            "jogador_origem_id": "1",
            "jogador_destino_id": "2",
            "pokemon_oferecido_id": "1",
            "pokemon_desejado_id": "99",
        })
        assert resp.status_code == 400

    def test_nivel_insuficiente_retorna_400(self, client, monkeypatch):
        ash = Jogador(1, "Ash")
        misty = Jogador(2, "Misty")
        fraco = Pokemon(1, "Pidgey", "disponivel", 3)
        forte = Pokemon(2, "Dragonite", "disponivel", 50)
        ash.pokemons.append(fraco)
        misty.pokemons.append(forte)
        monkeypatch.setattr(main, "jogadores", {1: ash, 2: misty})
        monkeypatch.setattr(main, "pokemons_disponiveis", {1: fraco, 2: forte})

        resp = client.post("/proposta", json={
            "jogador_origem_id": "1",
            "jogador_destino_id": "2",
            "pokemon_oferecido_id": "1",
            "pokemon_desejado_id": "2",
        })
        assert resp.status_code == 400

    def test_pokemon_ocupado_retorna_400(self, client, monkeypatch):
        ash = Jogador(1, "Ash")
        misty = Jogador(2, "Misty")
        ocupado = Pokemon(1, "Pikachu", "ocupado", 10)
        staryu = Pokemon(2, "Staryu", "disponivel", 8)
        ash.pokemons.append(ocupado)
        misty.pokemons.append(staryu)
        monkeypatch.setattr(main, "jogadores", {1: ash, 2: misty})
        monkeypatch.setattr(main, "pokemons_disponiveis", {1: ocupado, 2: staryu})

        resp = client.post("/proposta", json={
            "jogador_origem_id": "1",
            "jogador_destino_id": "2",
            "pokemon_oferecido_id": "1",
            "pokemon_desejado_id": "2",
        })
        assert resp.status_code == 400

    def test_payload_vazio_retorna_422(self, client):
        resp = client.post("/proposta", json={})
        assert resp.status_code == 422

    def test_payload_com_campos_faltando_retorna_422(self, client):
        resp = client.post("/proposta", json={"jogador_origem_id": "1"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /propostas/{jogador_id}
# ---------------------------------------------------------------------------

class TestListarPropostas:
    def test_jogador_sem_propostas_retorna_lista_vazia(self, client):
        resp = client.get("/propostas/1")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_jogador_com_proposta_recebida(self, client):
        ash = main.jogadores[1]
        misty = main.jogadores[2]
        pikachu = main.pokemons_disponiveis[1]
        staryu = main.pokemons_disponiveis[2]
        troca = Troca("uuid-test", ash, misty, pikachu, staryu)
        misty.propostas_recebidas.append(troca)

        resp = client.get("/propostas/2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["pokemon_oferecido"] == "Pikachu"
        assert data[0]["pokemon_desejado"] == "Staryu"

    def test_jogador_inexistente_retorna_404(self, client):
        resp = client.get("/propostas/99")
        assert resp.status_code == 404

    def test_resposta_contem_campos_esperados(self, client):
        ash = main.jogadores[1]
        misty = main.jogadores[2]
        pikachu = main.pokemons_disponiveis[1]
        staryu = main.pokemons_disponiveis[2]
        troca = Troca("uuid-campos", ash, misty, pikachu, staryu)
        misty.propostas_recebidas.append(troca)

        resp = client.get("/propostas/2")
        proposta = resp.json()[0]
        campos = {"id", "jogador_origem", "jogador_destino", "pokemon_oferecido", "pokemon_desejado", "status"}
        assert campos.issubset(set(proposta.keys()))


# ---------------------------------------------------------------------------
# POST /proposta/{id_proposta}/aceitar
# ---------------------------------------------------------------------------

class TestAceitarProposta:
    def test_aceitar_sucesso(self, client):
        with patch("main.atualizar_status_proposta"):
            resp = client.post("/proposta/uuid-123/aceitar")
        assert resp.status_code == 200
        assert resp.json()["mensagem"] == "Proposta aceita com sucesso"

    def test_atualizar_status_chamado_com_argumentos_corretos(self, client):
        with patch("main.atualizar_status_proposta") as mock_atualizar:
            client.post("/proposta/uuid-abc/aceitar")
        mock_atualizar.assert_called_once()
        args = mock_atualizar.call_args[0]
        assert args[0] == "uuid-abc"
        assert args[1] == "aceita"

    def test_proposta_inexistente_retorna_400(self, client):
        with patch("main.atualizar_status_proposta",
                   side_effect=Exception("Proposta não encontrada.")):
            resp = client.post("/proposta/nao-existe/aceitar")
        assert resp.status_code == 400
        assert "Proposta não encontrada." in resp.json()["detail"]

    def test_arquivo_nao_encontrado_retorna_400(self, client):
        with patch("main.atualizar_status_proposta",
                   side_effect=Exception("Arquivo de propostas não encontrado.")):
            resp = client.post("/proposta/qualquer/aceitar")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# GET /jogador/{jogador_id}
# ---------------------------------------------------------------------------

class TestObterJogador:
    def test_jogador_existente_retorna_dados(self, client):
        resp = client.get("/jogador/1")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == 1
        assert body["nome"] == "Ash"
        assert "Pikachu" in body["pokemons"]

    def test_jogador_inexistente_retorna_404(self, client):
        resp = client.get("/jogador/99")
        assert resp.status_code == 404

    def test_resposta_contem_campos_obrigatorios(self, client):
        resp = client.get("/jogador/2")
        body = resp.json()
        assert "id" in body
        assert "nome" in body
        assert "pokemons" in body
        assert "propostas_recebidas" in body

    def test_jogador_com_proposta_recebida_inclui_na_resposta(self, client):
        ash = main.jogadores[1]
        misty = main.jogadores[2]
        pikachu = main.pokemons_disponiveis[1]
        staryu = main.pokemons_disponiveis[2]
        troca = Troca("uuid-jog", ash, misty, pikachu, staryu)
        ash.propostas_recebidas.append(troca)

        resp = client.get("/jogador/1")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["propostas_recebidas"]) == 1


# ---------------------------------------------------------------------------
# GET /topicos_mqtt
# ---------------------------------------------------------------------------

class TestTopicosMqtt:
    def test_retorna_topico_proposta(self, client):
        resp = client.get("/topicos_mqtt")
        assert resp.status_code == 200
        assert "proposta" in resp.json()

    def test_retorna_topico_aceitacao(self, client):
        resp = client.get("/topicos_mqtt")
        assert "aceitacao" in resp.json()

    def test_estrutura_completa_dos_topicos(self, client):
        resp = client.get("/topicos_mqtt")
        body = resp.json()
        assert body["proposta"] == "troca/{jogador_destino_id}"
        assert body["aceitacao"] == "troca/sucesso"
