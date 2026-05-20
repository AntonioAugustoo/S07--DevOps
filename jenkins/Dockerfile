# usa a imagem oficial do Jenkins como base
FROM jenkins/jenkins:lts            

USER root

# instalando docker pois o Jenkins precisa do cliente Docker para rodar comandos como docker build e docker push
RUN apt-get update && \
    apt-get install -y docker.io && \
    apt-get clean

# adiciona o usuário jenkins ao grupo docker
RUN usermod -aG docker jenkins       

# volta para o usuário jenkins para rodar o Jenkins normalmente(retira do Root)
USER jenkins                            