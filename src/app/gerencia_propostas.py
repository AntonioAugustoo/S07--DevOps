from app.models.troca import Troca
from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
cliente = MongoClient(MONGO_URL)
db = cliente["pokemon_trade"]
colecao_propostas = db["propostas"]

def salvar_proposta_json(proposta: Troca):
    colecao_propostas.insert_one({
        "id": proposta.id,
        "pokemon_oferecido": proposta.pokemon_oferecido.nome,
        "pokemon_desejado": proposta.pokemon_desejado.nome,
        "jogador_origem": proposta.jogador_origem.id,
        "jogador_destino": proposta.jogador_destino.id,
        "ativa": True,
        "resposta": "pendente"
    })

def atualizar_status_proposta(proposta_id, status, jogadores, pokemons_disponiveis, gerenciador):
    proposta_encontrada = colecao_propostas.find_one({"id": proposta_id})

    if not proposta_encontrada:
        raise Exception("Proposta não encontrada.")

    colecao_propostas.update_one(
        {"id": proposta_id},
        {"$set": {"resposta": status, "ativa": False}}
    )

    jogador_origem = jogadores.get(int(proposta_encontrada["jogador_origem"]))
    jogador_destino = jogadores.get(int(proposta_encontrada["jogador_destino"]))

    pokemon_oferecido = next((pk for pk in jogador_origem.pokemons if pk.nome == proposta_encontrada["pokemon_oferecido"]), None)
    pokemon_desejado = next((pk for pk in jogador_destino.pokemons if pk.nome == proposta_encontrada["pokemon_desejado"]), None)

    if not all([jogador_origem, jogador_destino, pokemon_oferecido, pokemon_desejado]):
        raise Exception("Dados inválidos para processar troca.")

    jogador_origem.pokemons.remove(pokemon_oferecido)
    jogador_destino.pokemons.remove(pokemon_desejado)
    jogador_origem.pokemons.append(pokemon_desejado)
    jogador_destino.pokemons.append(pokemon_oferecido)

    troca = Troca(
        id=proposta_id,
        jogador_origem=jogador_origem,
        jogador_destino=jogador_destino,
        pokemon_oferecido=pokemon_oferecido,
        pokemon_desejado=pokemon_desejado,
        status=True
    )

    for proposta in jogador_destino.propostas_recebidas:
        if proposta.id == proposta_id:
            proposta.status = True
            break

    gerenciador.analisar_proposta(troca)