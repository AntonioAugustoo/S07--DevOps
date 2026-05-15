from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import paho.mqtt.publish as publish
from app.services.validadores import ValidadorNivel, ValidadorStatus
from app.models.troca import Troca
from app.notifications.notificacao_jogador import NotificacaoJogador
from app.services.gerenciador_troca import GerenciadorDeTroca
from app.utils_carregamento import carregar_dados_do_json, carregar_propostas_json
from app.gerencia_propostas import salvar_proposta_json, atualizar_status_proposta

CAMINHO_JSON = "jogadores_pokemons_10.json"
gerenciador = GerenciadorDeTroca(NotificacaoJogador())
jogadores, pokemons_disponiveis = carregar_dados_do_json(CAMINHO_JSON)
carregar_propostas_json("propostas_troca.json", jogadores, pokemons_disponiveis, gerenciador)
print("Jogadores carregados:", jogadores.keys())

app = FastAPI(
    title="API de Troca de Cartas Pokémon",
    description="Endpoints REST com integração MQTT para trocas entre jogadores",
    version="1.0.0"
)

class PropostaInput(BaseModel):
    jogador_origem_id: str
    jogador_destino_id: str
    pokemon_oferecido_id: str
    pokemon_desejado_id: str

@app.post("/proposta")
def criar_proposta(proposta: PropostaInput):
    try:
        from uuid import uuid4
        jogador_origem = jogadores.get(int(proposta.jogador_origem_id))
        jogador_destino = jogadores.get(int(proposta.jogador_destino_id))
        if not jogador_origem or not jogador_destino:
            raise HTTPException(status_code=404, detail="Jogadores não encontrados")

        pokemon_oferecido = next((p for p in jogador_origem.pokemons if p.id == int(proposta.pokemon_oferecido_id)), None)
        pokemon_desejado = next((p for p in jogador_destino.pokemons if p.id == int(proposta.pokemon_desejado_id)), None)
        if not pokemon_oferecido or not pokemon_desejado:
            raise HTTPException(status_code=404, detail="Pokémon não encontrado")

        troca_temp = Troca("temp", jogador_origem, jogador_destino, pokemon_oferecido, pokemon_desejado)
        validador = ValidadorStatus(ValidadorNivel())
        if not validador.validar(troca_temp):
            raise HTTPException(status_code=400, detail="Proposta inválida por regras de validação")

        nova_troca = Troca(str(uuid4()), jogador_origem, jogador_destino, pokemon_oferecido, pokemon_desejado)
        gerenciador.enviar_proposta(nova_troca)
        jogador_destino.propostas_recebidas.append(nova_troca)
        salvar_proposta_json(nova_troca)
        publish.single(f"troca/{proposta.jogador_destino_id}", payload="Nova proposta recebida", hostname="mosquitto")
        return {"mensagem": "Proposta criada com sucesso", "id_proposta": nova_troca.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/propostas/{jogador_id}")
def listar_propostas(jogador_id: str):
    jogador = jogadores.get(int(jogador_id))
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    return [p.to_dict() for p in jogador.propostas_recebidas]

@app.post("/proposta/{id_proposta}/aceitar")
def aceitar_proposta(id_proposta: str):
    try:
        atualizar_status_proposta(id_proposta, "aceita", jogadores, pokemons_disponiveis, gerenciador)
        publish.single("troca/sucesso", payload=f"Proposta {id_proposta} aceita", hostname="mosquitto")
        return {"mensagem": "Proposta aceita com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/jogador/{jogador_id}")
def obter_jogador(jogador_id: str):
    jogador = jogadores.get(int(jogador_id))
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    return jogador.to_dict()

@app.get("/topicos_mqtt")
def topicos_mqtt():
    return {
        "proposta": "troca/{jogador_destino_id}",
        "aceitacao": "troca/sucesso"
    }