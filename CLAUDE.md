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

### Running the full stack via Docker Compose
```bash
docker compose up
```
Requires a `.env` file — copy `.env.example` and fill in credentials. API docs at http://localhost:8000/docs, Jenkins at http://localhost:8080, SonarQube at http://localhost:9000.

### Triggering the Jenkins pipeline manually (via API)
```bash
PASS=$(docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword)
COOKIE=$(mktemp)
CRUMB=$(curl -s -u "admin:$PASS" -c "$COOKIE" http://localhost:8080/crumbIssuer/api/json | python3 -c "import sys,json; print(json.load(sys.stdin)['crumb'])")
curl -s -u "admin:$PASS" -b "$COOKIE" -H "Jenkins-Crumb: $CRUMB" -X POST http://localhost:8080/job/pokemon-api-pipeline/build
```

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

## CI/CD Pipeline

### Pipeline stages (Jenkinsfile)
1. **Testes** — runs `pytest` in a `python:3.12-slim` container with `--cov-fail-under=90`; archives `test-results/`
2. **SonarQube Analysis** — skipped unless `SONAR_HOST_URL` env var is set; reads coverage from `test-results/coverage.xml`
3. **Quality Gate** — `waitForQualityGate abortPipeline: true`; SonarQube stages are gated so Docker push never runs if QG fails
4. **Build / Empacotamento** — tarballs `src/`, `requirements.txt`, `Dockerfile.python` as a versioned artifact
5. **Build Docker Image** — skipped unless `DOCKER_HUB_USER` is set
6. **Push Docker Hub** — pushes `:BUILD_NUMBER` and `:latest` tags
7. **post** — sends email via `scripts/send_email.sh` using `curl smtp://`; silently skips if `SMTP_HOST` is unset

### Infrastructure containers
| Container | Dockerfile | Role |
|---|---|---|
| `pokemon-api` | `Dockerfile.python` | FastAPI app |
| `mosquitto` | Docker Hub | MQTT broker |
| `sonarqube` | `Dockerfile.sonarqube` | Code quality analysis |
| `sonarqube-db` | Docker Hub (postgres:16) | SonarQube persistence |
| `jenkins` | `Dockerfile.jenkins` | Jenkins LTS + sonar-scanner CLI + Docker socket |

### Jenkins configuration
- **Plugins**: defined in `jenkins/plugins.txt`, installed at image build via `jenkins-plugin-cli`
- **JCasC**: `jenkins/jenkins.yaml` is copied to `/usr/share/jenkins/casc_configs/` (not `jenkins_home` — that path is a volume and would hide the file). Credentials and SonarQube server are configured via env var substitution (`${SONAR_TOKEN}`, `${DOCKER_HUB_USER}`, `${DOCKER_HUB_PASS}`)
- **Local checkout**: Jenkins has `JAVA_OPTS=-Dhudson.plugins.git.GitSCM.ALLOW_LOCAL_CHECKOUT=true` to allow `file:///workspace` git URLs during local testing; the `docker-compose.yml` mounts `.:/workspace:ro` into the Jenkins container for this purpose

### SonarQube webhook
`waitForQualityGate` requires SonarQube to POST back to Jenkins. Register once after first startup:
```bash
curl -s -u admin:admin -X POST http://localhost:9000/api/webhooks/create \
  -d "name=Jenkins" -d "url=http://jenkins:8080/sonarqube-webhook/"
```

### Required `.env` variables
`DOCKER_HUB_USER`, `DOCKER_HUB_PASS`, `IMAGE_NAME`, `SONAR_TOKEN`, `SONAR_HOST_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` — and optionally `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `NOTIFICATION_EMAIL` for email notifications.
