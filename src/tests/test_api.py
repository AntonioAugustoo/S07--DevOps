import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.models.jogador import Jogador
from app.models.pokemon import Pokemon
from app.models.troca import Troca
from app.services.gerenciador_troca import GerenciadorDeTroca
from app.notifications.notificacao_jogador import NotificacaoJogador

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


class TestCriarProposta:
    def test_sucesso(self, client):
        with patch("main.salvar_proposta_json") as mock_save:
            resp = client.post("/proposta", json={"jogador_origem_id": "1", "jogador_destino_id": "2",
                                                   "pokemon_oferecido_id": "1", "pokemon_desejado_id": "2"})
        assert resp.status_code == 200
        assert "id_proposta" in resp.json() and resp.json()["mensagem"] == "Proposta criada com sucesso"
        mock_save.assert_called_once()
        assert len(main.jogadores[2].propostas_recebidas) == 1

    def test_erros_de_validacao(self, client):
        casos_400 = [
            {"jogador_origem_id": "99", "jogador_destino_id": "2", "pokemon_oferecido_id": "1", "pokemon_desejado_id": "2"},
            {"jogador_origem_id": "1", "jogador_destino_id": "99", "pokemon_oferecido_id": "1", "pokemon_desejado_id": "2"},
            {"jogador_origem_id": "1", "jogador_destino_id": "2", "pokemon_oferecido_id": "99", "pokemon_desejado_id": "2"},
            {"jogador_origem_id": "1", "jogador_destino_id": "2", "pokemon_oferecido_id": "1", "pokemon_desejado_id": "99"},
        ]
        for payload in casos_400:
            assert client.post("/proposta", json=payload).status_code == 400

        assert client.post("/proposta", json={}).status_code == 422
        assert client.post("/proposta", json={"jogador_origem_id": "1"}).status_code == 422


class TestListarEAceitarPropostas:
    def test_listar_propostas(self, client):
        assert client.get("/propostas/1").json() == []
        assert client.get("/propostas/99").status_code == 404

        ash = main.jogadores[1]
        misty = main.jogadores[2]
        pikachu = main.pokemons_disponiveis[1]
        staryu = main.pokemons_disponiveis[2]
        misty.propostas_recebidas.append(Troca("uuid-test", ash, misty, pikachu, staryu))

        resp = client.get("/propostas/2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["pokemon_oferecido"] == "Pikachu"
        campos = {"id", "jogador_origem", "jogador_destino", "pokemon_oferecido", "pokemon_desejado", "status"}
        assert campos.issubset(set(data[0].keys()))

    def test_aceitar_proposta(self, client):
        with patch("main.atualizar_status_proposta") as mock_atualizar:
            resp = client.post("/proposta/uuid-abc/aceitar")
        assert resp.status_code == 200
        assert resp.json()["mensagem"] == "Proposta aceita com sucesso"
        args = mock_atualizar.call_args[0]
        assert args[0] == "uuid-abc" and args[1] == "aceita"

        with patch("main.atualizar_status_proposta", side_effect=Exception("Proposta não encontrada.")):
            resp = client.post("/proposta/nao-existe/aceitar")
        assert resp.status_code == 400
        assert "Proposta não encontrada." in resp.json()["detail"]


class TestObterJogador:
    def test_obter_jogador(self, client):
        resp = client.get("/jogador/1")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == 1 and body["nome"] == "Ash"
        assert "Pikachu" in body["pokemons"]
        assert {"id", "nome", "pokemons", "propostas_recebidas"}.issubset(set(body.keys()))

        assert client.get("/jogador/99").status_code == 404

        ash = main.jogadores[1]
        misty = main.jogadores[2]
        ash.propostas_recebidas.append(
            Troca("uuid-jog", ash, misty, main.pokemons_disponiveis[1], main.pokemons_disponiveis[2])
        )
        assert len(client.get("/jogador/1").json()["propostas_recebidas"]) == 1


class TestTopicosMqtt:
    def test_topicos_mqtt(self, client):
        resp = client.get("/topicos_mqtt")
        assert resp.status_code == 200
        body = resp.json()
        assert body["proposta"] == "troca/{jogador_destino_id}"
        assert body["aceitacao"] == "troca/sucesso"
