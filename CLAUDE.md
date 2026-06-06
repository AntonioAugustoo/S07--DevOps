# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Pokémon card trading system built as a DevOps project. FastAPI handles REST routes, MQTT (Mosquitto broker) provides async messaging between players, and proposals are persisted in MongoDB. The CI/CD pipeline runs via Jenkins in Docker, with SonarQube quality gates before Docker Hub publish.

## Commands

### Running tests

```bash
# All tests with coverage (run from repo root)
pytest --cov=app --cov-report=term-missing

# Single test file
pytest src/tests/test_api.py

# Single test by name
pytest src/tests/test_api.py::TestCriarProposta::test_sucesso
```

`pytest.ini` sets `testpaths = src/tests` and `pythonpath = src`, so coverage must target `app` (not `src`). Tests require no running services — MongoDB and MQTT are fully mocked.

### Running tests inside Docker (same environment as Jenkins)

```bash
docker run --rm -v "$(pwd)":/app -w /app python:3.12-slim \
  sh -c "pip install -r requirements.txt -q && cd src && python -m pytest tests/ -v"
```

### Running the API locally

```bash
cd src && MONGO_URI=mongodb://localhost:27017/ uvicorn main:app --host 0.0.0.0 --port 8000
```

### Running the full stack via Docker Compose

```bash
cp .env.example .env   # fill in DOCKER_HUB_USER, DOCKER_HUB_PASS, and Postgres credentials
docker compose up
```

- API: <http://localhost:8000/docs>
- Jenkins: <http://localhost:8080> — login `admin` / `admin` (no wizard)
- SonarQube: <http://localhost:9000> — login `admin` / `admin`

The `sonarqube-init` service runs once after SonarQube becomes healthy and:

1. Disables forced authentication (allows sonar-scanner without a token)
2. Registers the webhook `http://jenkins:8080/sonarqube-webhook/` (required for `waitForQualityGate`)

### Triggering the Jenkins pipeline manually (via API)

```bash
COOKIE=$(mktemp)
CRUMB=$(curl -s -u "admin:admin" -c "$COOKIE" http://localhost:8080/crumbIssuer/api/json | python3 -c "import sys,json; print(json.load(sys.stdin)['crumb'])")
curl -s -u "admin:admin" -b "$COOKIE" -H "Jenkins-Crumb: $CRUMB" -X POST http://localhost:8080/job/pokemon-api-pipeline/build
```

## Architecture

### Application state

State lives in two layers:

- **In-memory dicts** (`jogadores`, `pokemons_disponiveis`) — loaded at startup from `src/jogadores_pokemons_10.json` via `carregar_dados_do_json`. These are module-level globals in `src/main.py`; tests replace them with `monkeypatch`.
- **MongoDB** (`src/database.py`) — `colecao_propostas` in the `pokemon_trades` database. `salvar_proposta_json` inserts new proposals; `atualizar_status_proposta` queries and updates them. On startup, `main.py` replays active proposals from MongoDB into the in-memory state (wrapped in `try/except` so the app boots without MongoDB).

Proposals are tracked in two separate in-memory lists simultaneously:

- `gerenciador.propostas` — used by `GerenciadorDeTroca`
- `jogador.propostas_recebidas` — used by `GET /propostas/{jogador_id}`

### API endpoints (`src/main.py`)

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/proposta` | Validate → persist to MongoDB → publish MQTT |
| `GET` | `/propostas/{jogador_id}` | List proposals received by a player |
| `POST` | `/proposta/{id_proposta}/aceitar` | Swap Pokémon ownership in memory + update MongoDB |
| `GET` | `/jogador/{jogador_id}` | Get player info with their Pokémon |
| `GET` | `/topicos_mqtt` | List MQTT topics used |

### Design patterns

- **Chain of Responsibility** — `ValidadorBase → ValidadorNivel → ValidadorStatus` in `src/app/services/validadores.py`. Chain order matters: `ValidadorStatus(ValidadorNivel())` — status is checked first, level second.
- **Decorator** — `NotificacaoDecorator` wraps `INotificacao` implementations for logging.
- **Factory** — `NotificacaoFactory` (currently only creates `NotificacaoJogador`).

### Trade validation rules

1. Offered Pokémon must have `status == "disponivel"` (`ValidadorStatus`)
2. Offered Pokémon's `nivel >= nivel` of desired Pokémon (`ValidadorNivel`)

### MQTT

Fire-and-forget via `paho.mqtt.publish.single` with `hostname="mosquitto"`. All tests mock this with `patch("paho.mqtt.publish.single")`.

### Test layout and mocking strategy

- `conftest.py` calls `os.chdir` to `src/` at module level for relative JSON paths.
- **MongoDB mock**: `conftest.py` patches `database.colecao_propostas` with a `MagicMock` at module level (before test files import `main`). This is necessary because `main.py` runs `colecao_propostas.find()` at import time. Individual test classes that test `gerencia_propostas.py` patch `app.gerencia_propostas.colecao_propostas` directly.
- Coverage excludes `mqtt_servidor.py` and `mqtt_cliente.py` (see `src/.coveragerc`).

## CI/CD Pipeline

### Pipeline stages (Jenkinsfile)

1. **Testes** — `pytest` in `python:3.12-slim` with `--cov-fail-under=90`; archives `test-results/junit.xml` and `coverage.xml`
2. **SonarQube Analysis** — conditional on `SONAR_HOST_URL` env var; reads `test-results/coverage.xml`
3. **Quality Gate** — `waitForQualityGate abortPipeline: true`; downstream stages are blocked if QG fails
4. **Build / Empacotamento** — tarballs `src/`, `requirements.txt`, `Dockerfile.python` as `pokemon-api-build-{N}.tar.gz`
5. **Build Docker Image** — conditional on `DOCKER_HUB_USER`; tags `:BUILD_NUMBER` and `:latest`
6. **Push Docker Hub** — conditional on `DOCKER_HUB_USER`
7. **post** — `scripts/send_email.sh` via `curl smtp://`; silently skips if `SMTP_HOST` is unset

### Infrastructure containers

| Container | Dockerfile | Role |
| --- | --- | --- |
| `pokemon-api` | `Dockerfile.python` | FastAPI app |
| `mosquitto` | Docker Hub | MQTT broker |
| `mongodb` | `Dockerfile.mongodb` | MongoDB for proposal persistence |
| `sonarqube` | `Dockerfile.sonarqube` | Code quality analysis |
| `sonarqube-db` | Docker Hub (`postgres:16`) | SonarQube persistence |
| `sonarqube-init` | Docker Hub (`alpine:3.20`) | One-shot: registers webhook + disables forced auth |
| `jenkins` | `Dockerfile.jenkins` | Jenkins LTS + sonar-scanner CLI + Docker socket |

### Jenkins configuration

- **Plugins**: `jenkins/plugins.txt`, installed at image build via `jenkins-plugin-cli`
- **JCasC**: `jenkins/jenkins.yaml` copied to `/usr/share/jenkins/casc_configs/` (not `jenkins_home` — that path is a volume and would hide the file). Credentials and SonarQube server use env var substitution (`${SONAR_TOKEN}`, `${DOCKER_HUB_USER}`, `${DOCKER_HUB_PASS}`).
- **Local checkout**: `JAVA_OPTS=-Dhudson.plugins.git.GitSCM.ALLOW_LOCAL_CHECKOUT=true` + `.:/workspace:ro` mount enables `file:///workspace` git URLs. JCasC configures the job to track `*/main` and `*/feature/pipeline-ci-cd`.

### SonarQube webhook

Registered automatically by `sonarqube-init`. To register manually:

```bash
curl -s -u admin:admin -X POST http://localhost:9000/api/webhooks/create \
  -d "name=Jenkins" -d "url=http://jenkins:8080/sonarqube-webhook/"
```

### Required `.env` variables

`DOCKER_HUB_USER`, `DOCKER_HUB_PASS`, `IMAGE_NAME`, `SONAR_TOKEN`, `SONAR_HOST_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `MONGO_URI`, `MONGO_DB` — and optionally `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `NOTIFICATION_EMAIL` for email notifications.
