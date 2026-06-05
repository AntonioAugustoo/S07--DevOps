# <img src="https://cdn2.steamgriddb.com/icon_thumb/9a9edc1720f84b8907d3b7f81c1fbb50.png" width="40" style="vertical-align: middle; margin-right: 6px;" /> Projeto de DevOps — Sistema de Trocas de Cartas Pokémon

## 🌟 Visão Geral

Este projeto demonstra o domínio de práticas modernas de DevOps através da implementação de um sistema distribuído de trocas de cartas Pokémon. O objetivo principal é automatizar todo o ciclo de vida do software — desde o desenvolvimento e execução de testes até o deploy em containers e notificação de status.

O sistema utiliza **FastAPI** para gerenciar as rotas de trocas, **MQTT (Mosquitto)** para comunicação assíncrona entre jogadores e **arquivos JSON** para persistência de propostas. A infraestrutura completa sobe com um único comando via Docker Compose, incluindo Jenkins CI/CD e análise de qualidade via SonarQube.

---

## 🐳 Imagem no Docker Hub

A imagem da aplicação é publicada automaticamente pelo pipeline Jenkins a cada build bem-sucedido:

**[hub.docker.com/r/matheusvhs/pokemon-api](https://hub.docker.com/repository/docker/matheusvhs/pokemon-api/general)**

```bash
docker pull matheusvhs/pokemon-api:latest
```

---

## 🛠️ Stack Tecnológica & Infraestrutura

A infraestrutura utiliza **6 containers** orquestrados via Docker Compose:

| # | Container | Origem | Função |
| --- | --- | --- | --- |
| 1 | `pokemon-api` | Dockerfile local (`Dockerfile.python`) | Backend FastAPI |
| 2 | `mosquitto` | Docker Hub (`eclipse-mosquitto:2`) | Broker MQTT para mensageria assíncrona |
| 3 | `sonarqube` | Dockerfile local (`Dockerfile.sonarqube`) | Análise de qualidade de código |
| 4 | `sonarqube-db` | Docker Hub (`postgres:16-alpine`) | Banco de dados do SonarQube |
| 5 | `jenkins` | Dockerfile local (`Dockerfile.jenkins`) | Orquestrador do pipeline CI/CD |
| 6 | `sonarqube-init` | Docker Hub (`alpine:3.20`) | Configura SonarQube automaticamente na primeira execução |

**Comunicação entre serviços:**
- `pokemon-api` ↔ `mosquitto` via MQTT (porta 1883)
- `sonarqube` ↔ `sonarqube-db` via JDBC/PostgreSQL
- `jenkins` ↔ `sonarqube` via API REST (Quality Gate)

**Volumes persistentes:** `jenkins_home`, `sonarqube_data`, `sonarqube_extensions`, `sonarqube_logs`, `postgresql_data`

---

## 🚀 Pipeline CI/CD (Jenkinsfile)

O Jenkins monitora este repositório via webhook. A cada push na branch `main`, executa automaticamente:

| Stage | Descrição |
| --- | --- |
| **Testes** | `pytest` com cobertura ≥ 90%; artefato `junit.xml` + `coverage.xml` arquivados |
| **SonarQube Analysis** | Análise estática com `sonar-scanner` (condicional: exige `SONAR_HOST_URL`) |
| **Quality Gate** | Aguarda resultado do SonarQube; aborta o pipeline se falhar |
| **Build / Empacotamento** | Gera `pokemon-api-build-{N}.tar.gz` e arquiva como artefato no Jenkins |
| **Build Docker Image** | Constrói imagem com `Dockerfile.python` (condicional: exige `DOCKER_HUB_USER`) |
| **Push Docker Hub** | Publica `:BUILD_NUMBER` e `:latest` (condicional: exige `DOCKER_HUB_USER`) |
| **Notificação e-mail** | `scripts/send_email.sh` envia resultado via SMTP (condicional: exige `SMTP_HOST`) |

---

## 📦 Instalação e Execução

### Pré-requisitos

- Docker Engine ≥ 24
- Docker Compose v2

### 1. Clone o repositório

```bash
git clone https://github.com/AntonioAugustoo/S07--DevOps.git
cd S07--DevOps
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` e preencha os valores:

```env
# Docker Hub (necessário para push da imagem)
DOCKER_HUB_USER=seu_usuario
DOCKER_HUB_PASS=seu_token

# SonarQube (opcional — habilita análise de qualidade)
SONAR_HOST_URL=http://sonarqube:9000
SONAR_TOKEN=

# SMTP (opcional — habilita notificações por e-mail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu@email.com
SMTP_PASS=senha_de_app
NOTIFICATION_EMAIL=destino@email.com

# Banco de dados interno do SonarQube
POSTGRES_USER=sonar
POSTGRES_PASSWORD=sonar
POSTGRES_DB=sonar
```

### 3. Suba a infraestrutura

```bash
docker compose up
```

O serviço `sonarqube-init` configura automaticamente o SonarQube e registra o webhook do Jenkins — nenhuma configuração manual necessária.

### Acessos

| Serviço | URL | Credenciais |
| --- | --- | --- |
| API (Swagger) | <http://localhost:8000/docs> | — |
| Jenkins | <http://localhost:8080> | `admin` / `admin` |
| SonarQube | <http://localhost:9000> | `admin` / `admin` |

### Disparar o pipeline manualmente (via API do Jenkins)

```bash
CRUMB=$(curl -s -u "admin:admin" http://localhost:8080/crumbIssuer/api/json | python3 -c "import sys,json; print(json.load(sys.stdin)['crumb'])")
curl -s -u "admin:admin" -H "Jenkins-Crumb: $CRUMB" -X POST http://localhost:8080/job/pokemon-api-pipeline/build
```

---

## 🔌 Endpoints da API

### Criar Proposta

**POST** `/proposta`
```json
{
  "jogador_origem_id": "string",
  "jogador_destino_id": "string",
  "pokemon_oferecido_id": "string",
  "pokemon_desejado_id": "string"
}
```

### Listar Propostas Recebidas

**GET** `/propostas/{jogador_id}`

### Aceitar Proposta

**POST** `/proposta/{id_proposta}/aceitar`

### Obter Jogador

**GET** `/jogador/{jogador_id}`

### Listar Tópicos MQTT

**GET** `/topicos_mqtt`

---

## ⚙️ Funcionalidades

- **Troca de Pokémon entre jogadores** — proposta, validação e aceite com troca de posse
- **Validação em cadeia** (Chain of Responsibility) — `ValidadorNivel` garante que o Pokémon oferecido tenha nível ≥ ao desejado; `ValidadorStatus` garante que esteja disponível
- **Notificações assíncronas via MQTT** — cada proposta publica mensagem no broker Mosquitto
- **Pipeline CI/CD totalmente automatizado** — testes, qualidade, empacotamento, publicação e notificação sem intervenção manual
- **Infraestrutura reproduzível** — todas as dependências (plugins Jenkins, sonar-scanner, configurações JCasC) instaladas via Dockerfile e scripts; nada configurado pela GUI

---

## 🤖 Uso Transparente de IA

As ferramentas de IA utilizadas no projeto foram:

| Ferramenta | Uso principal |
| --- | --- |
| **Claude (Anthropic)** | Estruturação do `Dockerfile.jenkins`, `jenkins.yaml` (JCasC), `docker-compose.yml`, debug de pipeline, revisão de testes |
| **GitHub Copilot** | Autocomplete em testes unitários e nas rotas FastAPI |

### Exemplos reais de prompts

**Prompt 1** — configuração do JCasC para zero-config:
> "No meu `jenkins.yaml` eu quero que o job já seja criado automaticamente apontando para o `Jenkinsfile` do repositório local montado em `/workspace`. Como fazer isso via JCasC sem precisar da interface gráfica?"

*Resultado:* A resposta trouxe o bloco `jobs.script` com `cpsScm` + `git remote url('file:///workspace')`. Foi aceito com ajuste no `scriptPath` e adição das branches `*/main` e `*/feature/pipeline-ci-cd`.

---

**Prompt 2** — stages condicionais no Jenkinsfile:
> "Quero que os stages de SonarQube e Docker Hub só rodem se as variáveis de ambiente `SONAR_HOST_URL` e `DOCKER_HUB_USER` estiverem definidas. Como usar `when { expression { ... } }` no Declarative Pipeline?"

*Resultado:* A resposta foi aceita integralmente. Permitiu que o pipeline funcione em ambientes sem Docker Hub ou SonarQube configurados sem falhar.

---

**Prompt 3** — service healthcheck para o SonarQube:
> "Meu container `sonarqube-init` roda antes do SonarQube estar pronto e falha. Como configurar um `healthcheck` no docker-compose para o SonarQube e fazer o `sonarqube-init` depender dele com `condition: service_healthy`?"

*Resultado:* A sugestão do `healthcheck` com `curl -sf http://localhost:9000/api/system/status` foi aceita. O `start_period: 120s` foi ajustado manualmente após observar o tempo real de inicialização do SonarQube.

### O que não foi feito por IA

- Modelagem do domínio (classes `Jogador`, `Pokemon`, `Troca`, padrões Chain of Responsibility, Decorator e Factory)
- Lógica de negócio das validações e troca de posse dos Pokémon
- Estrutura dos testes e casos de teste (`conftest.py`, fixtures, monkeypatch)
- Decisão de arquitetura (MQTT fire-and-forget, persistência em JSON, separação `gerencia_propostas.py`)

### Dinâmica de uso

IA foi usada principalmente em **pair programming** para configurações de infraestrutura (onde erros de sintaxe têm custo alto) e para debug de mensagens de erro do Jenkins e Docker Compose. O código de aplicação e os testes foram escritos manualmente.

---

## 👥 Equipe

- **Antonio Augusto** — Software Engineer (INATEL)
- **Otavio Augusto Lima** — Software Engineer (INATEL)
- **Matheus Vieira Honório de Souza** — Software Engineer (INATEL)
- **Otávio Oliveira Jimenez** — Software Engineer (INATEL)

---

## 📄 Licença

MIT
