# <img src="https://cdn2.steamgriddb.com/icon_thumb/9a9edc1720f84b8907d3b7f81c1fbb50.png" width="40" style="vertical-align: middle; margin-right: 6px;" /> Projeto de DevOps -- Sistema de Trocas de Cartas Pokémon

## 🌟 Visão Geral

Este projeto demonstra o domínio de práticas modernas de DevOps através da implementação de um sistema distribuído de trocas de cartas Pokémon. O objetivo principal é automatizar todo o ciclo de vida do software, desde o desenvolvimento e execução de testes até o deploy em containers e notificação de status.  

O sistema utiliza FastAPI para gerenciar as rotas de trocas, MQTT (Mosquitto) para comunicação assíncrona entre os jogadores (propostas e aceitações) e um banco de dados (NOME DO BANCO) para cache de propostas em tempo real, garantindo alta performance e persistência de dados através de volumes.


## 🛠️ Stack Tecnológica & Infraestrutura
Para atender ao requisito de 4+ Containers e Comunicação entre Serviços, a infraestrutura foi desenhada da seguinte forma:

Container 1: api-pokemon (Dockerfile Local) — Backend em FastAPI.

Container 2: mqtt-broker (Docker Hub) — Mosquitto para mensageria assíncrona.

Container 3: AINDA A PREENCHER (Banco a escolher)

Container 4: jenkins-server (Docker Hub) — Orquestrador do pipeline (rodando em modo container).


## 🚀 Pipeline CI/CD (Jenkinsfile)
O Jenkins configurado no container monitora este repositório. Ao realizar um push, ele executa automaticamente:
* Execução de testes unitários(>90% de cobertura). 
* Build e armazenamento de artefatos (relatórios e pacote). 
* Push da imagem para o Docker Hub. 
* Envio de notificação de sucesso/falha por e-mail.


## 📦 Como Executar

Instalação e Execução:

* Clone o repositório na organização do seu time no GitHub.  
* Certifique-se de ter o Docker e Docker Compose instalados.  
* Suba a infraestrutura completa com um único comando:
```bash
docker-compose up
```
* Acesse a documentação interativa da API (Swagger) em: http://localhost:8000/docs

## 🔌 Endpoints da API

### ✅ Criar Proposta
**POST** `/proposta`
```json
{
  "jogador_origem_id": "string",
  "jogador_destino_id": "string",
  "pokemon_oferecido_id": "string",
  "pokemon_desejado_id": "string"
}
```

### 📥 Listar Propostas Recebidas
**GET** `/propostas/{jogador_id}`

### 🤝 Aceitar Proposta
**POST** `/proposta/{id_proposta}/aceitar`

### 👤 Obter Jogador
**GET** `/jogador/{jogador_id}`

## ⚙️ Configuração e Setup

> Instruções detalhadas de configuração serão adicionadas em breve.

## 🤖 Uso Transparente de IA

Conforme exigido pelos critérios de avaliação, declaramos o uso de ferramentas de IA no desenvolvimento deste projeto:




👥 Equipe e Contato
* Antonio Augusto — Software Engineer (INATEL)
* Otavio Augusto Lima — Software Engineer (INATEL)
* Matheus Vieira Honório de Souza — Software Engineer (INATEL)
* Otávio Oliveira Jimenez — Software Engineer (INATEL)




## 📄 Licença
Projeto em desenvolvimento. Todos os direitos reservados.