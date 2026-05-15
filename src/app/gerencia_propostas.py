import json
from app.models.troca import Troca

CAMINHO_PROPOSTAS = "propostas_troca.json"

def salvar_proposta_json(proposta: Troca):
    try:
        with open(CAMINHO_PROPOSTAS, "r") as f:
            propostas = json.load(f)
    except FileNotFoundError:
        propostas = []

    propostas.append({
        "id": proposta.id,
        "pokemon_oferecido": proposta.pokemon_oferecido.nome,
        "pokemon_desejado": proposta.pokemon_desejado.nome,
        "jogador_origem": proposta.jogador_origem.id,
        "jogador_destino": proposta.jogador_destino.id,
        "ativa": True,
        "resposta": "pendente"
    })

    with open(CAMINHO_PROPOSTAS, "w") as f:
        json.dump(propostas, f, indent=4)

def atualizar_status_proposta(proposta_id, status, jogadores, pokemons_disponiveis, gerenciador):
    try:
        with open("propostas_troca.json", "r") as f:
            propostas = json.load(f)
    except FileNotFoundError:
        raise Exception("Arquivo de propostas não encontrado.")

    proposta_encontrada = None
    for p in propostas:
        if p["id"] == proposta_id:
            p["resposta"] = status
            p["ativa"] = False
            proposta_encontrada = p
            break

    if not proposta_encontrada:
        raise Exception("Proposta não encontrada.")

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

    # Atualizar proposta em memória
    for proposta in jogador_destino.propostas_recebidas:
        if proposta.id == proposta_id:
            proposta.status = True
            break

    gerenciador.analisar_proposta(troca)

    with open("propostas_troca.json", "w") as f:
        json.dump(propostas, f, indent=4)

        json.dump(propostas, f, indent=4)