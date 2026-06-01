# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Pokémon card trading system built as a DevOps project. FastAPI handles REST routes, MQTT (Mosquitto broker) provides async messaging between players, and state is persisted via JSON files. The CI/CD pipeline runs via Jenkins in Docker.

## Commands

### Running tests
```bash
# All tests with coverage (run from repo root)
pytest --cov=src --cov-report=term-missing

# Single test file
pytest src/tests/test_api.py

# Single test by name
pytest src/tests/test_api.py::TestCriarProposta::test_sucesso
```

### Running the API locally
```bash
cd src && uvicorn main:app --host 0.0.0.0 --port 8000
```

### Running via Docker
```bash
docker-compose up
```
API docs available at http://localhost:8000/docs after startup.

## Architecture

### Application state (in-memory + JSON)
The app has **no database** — state lives in two places:
- **In-memory dicts** (`jogadores`, `pokemons_disponiveis`) loaded at startup from `src/jogadores_pokemons_10.json`
- **`src/propostas_troca.json`** — append-only JSON file for trade proposals, reloaded on startup

Both are module-level globals in `src/main.py`. Tests use `monkeypatch` to replace these globals.

### Design patterns
- **Chain of Responsibility** — `ValidadorBase → ValidadorNivel → ValidadorStatus` in `src/app/services/validadores.py`. Validators chain via `super().validar(troca)`.
- **Decorator** — `NotificacaoDecorator` wraps `INotificacao` implementations for logging.
- **Factory** — `NotificacaoFactory` (currently only creates `NotificacaoJogador`).

### MQTT integration
MQTT publishes fire-and-forget via `paho.mqtt.publish.single` with `hostname="mosquitto"` (Docker service name). All tests mock this with `patch("paho.mqtt.publish.single")` — MQTT is not needed for tests.

### Trade validation rules
A trade is valid when:
1. The offered Pokémon has `status == "disponivel"` (checked by `ValidadorStatus`)
2. The offered Pokémon's `nivel >= nivel` of the desired Pokémon (checked by `ValidadorNivel`)

### Test layout
Tests live in `src/tests/`. `conftest.py` sets `os.chdir` to `src/` so relative JSON paths work. `pytest.ini` sets `pythonpath = src`, so imports use `from app.xxx import ...`.

Coverage excludes `mqtt_servidor.py` and `mqtt_cliente.py` (see `src/.coveragerc`).

### Infrastructure containers
| Container | Source | Role |
|---|---|---|
| `api-pokemon` | `./Dockerfile` | FastAPI app, copies `src/` to `/app` |
| `mqtt-broker` | Docker Hub (eclipse-mosquitto) | MQTT broker |
| `jenkins-server` | `./jenkins/Dockerfile` | Jenkins LTS + Docker client |
