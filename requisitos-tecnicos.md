# Requisitos Técnicos — Projeto S07 NP2
> INATEL · S07 Gerência de Configuração e Evolução de Software

## Contexto

O projeto deve demonstrar domínio de práticas DevOps modernas: containerização com Docker, automação de CI/CD com Jenkins e orquestração de múltiplos serviços com Docker Compose. O sistema deve ser de autoria própria do grupo (não pode ser o sistema usado pelo professor nas aulas).

---

## 1. Repositório e Versionamento

- Repositório **público** no GitHub (no time da matéria).
- Commits relevantes e significativos de **todos** os membros do grupo.
- Grupos de 4 a 6 integrantes.

---

## 2. Aplicação e Testes

- Sistema de software original (não o usado pelo professor).
- Cobertura de testes **≥ 90%** — unitários e/ou integração e/ou interface.
- Os testes devem ser executados dentro do pipeline Jenkins.

---

## 3. Dockerfile

- Jenkins deve rodar **em container** — proibido instalar diretamente na máquina.
- A imagem gerada deve ser correta e reproduzível.
- Qualquer dependência necessária para o pipeline deve ser instalada via **script ou Dockerfile** (nunca pela interface gráfica do Jenkins).

---

## 4. Pipeline Jenkins (Jenkinsfile)

O pipeline deve estar **inteiramente definido no `Jenkinsfile`**. A interface gráfica do Jenkins só pode ser usada para o checkout do código — todas as etapas devem estar no arquivo.

### Etapas obrigatórias

| Etapa | Descrição |
|---|---|
| **Testes** | Execução da suite de testes com geração de relatório |
| **Build / Empacotamento** | Geração do artefato final da aplicação |
| **Notificação por e-mail** | Envio de e-mail com informações da execução via script externo |

### Artefatos no Jenkins

- O **pacote** (build) deve ser armazenado como artefato no Jenkins.
- O **relatório de testes** deve ser armazenado como artefato no Jenkins.

### Notificação por e-mail

- Um script (linguagem livre) deve ser chamado para enviar o e-mail.
- O endereço de e-mail **não pode ser hardcoded** — deve ser lido de uma **variável de ambiente**.

### Restrições

- Proibido usar **GitHub Actions**.
- Proibido criar etapas do pipeline pela interface gráfica do Jenkins.

---

## 5. Docker Hub

- Criar uma imagem da aplicação a partir do `Dockerfile`.
- Publicar a imagem em: [https://hub.docker.com](https://hub.docker.com)
- Entregar o **link público da imagem** junto ao repositório no GitHub.

---

## 6. Docker Compose — mínimo de 4 containers

| Requisito | Detalhe |
|---|---|
| **Mínimo de containers** | 4 containers no total |
| **Mix de origens** | Pelo menos 1 container via `Dockerfile` local + pelo menos 1 puxado do Docker Hub |
| **Comunicação** | Pelo menos 2 containers devem se comunicar entre si |
| **Volumes** | Uso correto de volumes para persistir dados relevantes |

O `docker-compose.yml` deve subir a imagem publicada no Docker Hub e executar o pipeline completo.

> Referência de exemplos: https://github.com/docker/awesome-compose

---

## 7. README

O `README.md` do repositório deve conter:

- Instruções de **instalação**
- Instruções de **execução**
- Instruções de **uso**
- Descrição das **funcionalidades**
- Seção **"Uso de IA"** (ver seção abaixo)

---

## 8. Seção "Uso de IA" no README

Obrigatória. Deve conter:

- Modelos utilizados (ex.: Claude, GPT-4, Gemini, Copilot, Cursor…)
- Para quê cada modelo foi usado (Dockerfile, Jenkinsfile, scripts, testes, documentação, debugging, brainstorming…)
- **Pelo menos 3 exemplos reais de prompts** usados pelo grupo, indicando quais respostas foram aceitas, ajustadas ou descartadas
- Dinâmica de uso: individual, pair programming, revisão de configurações etc.
- O que **não** foi feito por IA — partes desenvolvidas manualmente

---

## 9. Entrega

- Link para o **repositório público no GitHub** enviado via tarefa no Teams.
- Link para a **imagem publicada no Docker Hub**.

---

## 10. Critérios de Eliminação

Os itens abaixo resultam em **nota zero**:

- Não comparecer na defesa.
- Commits claramente irrelevantes ao longo do semestre.
- Copiar configurações geradas por IA sem entender o que foi gerado.
- Usar a interface gráfica do Jenkins para criar etapas do pipeline (checkout é permitido).
- Clara discrepância de contribuição entre os integrantes.

---

## 11. Defesa (formato Q&A)

- Sem apresentação roteirizada — o professor fará perguntas diretas ao grupo.
- **Todos** os membros devem estar preparados para responder qualquer pergunta.
- O professor pode pedir para abrir o repositório, navegar por commits, mostrar o `Jenkinsfile`, executar o pipeline ao vivo.
- Respostas concretas (com arquivo, commit, log ou artefato) somam pontos.
- Tempo máximo: **20 minutos por grupo**.
