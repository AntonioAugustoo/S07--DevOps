import json
from app.models.jogador import Jogador
from app.models.pokemon import Pokemon

def carregar_dados_do_json(caminho_arquivo):
    jogadores = {}
    pokemons_disponiveis = {}

    with open(caminho_arquivo, "r") as f:
        dados = json.load(f)

    for j in dados["jogadores"]:
        jogador = Jogador(j["id"], j["nome"])
        jogadores[jogador.id] = jogador

    for p in dados["pokemons"]:
        pokemon = Pokemon(p["id"], p["nome"], p["status"], p["nivel"])
        pokemon.dono_id = p.get("dono_id")
        pokemons_disponiveis[pokemon.id] = pokemon

    
    # Associar Pokémon aos jogadores
    for pokemon in pokemons_disponiveis.values():
        dono_id = pokemon.dono_id
        if dono_id in jogadores:
            jogadores[dono_id].pokemons.append(pokemon)

    return jogadores, pokemons_disponiveis
    

from app.models.troca import Troca

def carregar_propostas_json(caminho, jogadores, pokemons_disponiveis, gerenciador):
    try:
        with open(caminho, "r") as f:
            propostas_data = json.load(f)
    except FileNotFoundError:
        propostas_data = []

    for p in propostas_data:
        jogador_origem = jogadores.get(p["jogador_origem"])
        jogador_destino = jogadores.get(p["jogador_destino"])
        pokemon_oferecido = next((pkmn for pkmn in pokemons_disponiveis.values() if pkmn.nome == p["pokemon_oferecido"]), None)
        pokemon_desejado = next((pkmn for pkmn in pokemons_disponiveis.values() if pkmn.nome == p["pokemon_desejado"]), None)

        if jogador_origem and jogador_destino and pokemon_oferecido and pokemon_desejado:
            proposta = Troca(
                id=p["id"],
                pokemon_oferecido=pokemon_oferecido,
                pokemon_desejado=pokemon_desejado,
                jogador_origem=jogador_origem,
                jogador_destino=jogador_destino,
                status=p["ativa"]
            )
            gerenciador.propostas.append(proposta)