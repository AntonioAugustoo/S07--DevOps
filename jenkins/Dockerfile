FROM jenkins/jenkins:lts

USER root

RUN apt-get update && \
    apt-get install -y docker.io curl unzip && \
    apt-get clean

RUN curl -sSL https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-6.2.1.4610-linux-x64.zip \
      -o /tmp/sonar-scanner.zip && \
    unzip /tmp/sonar-scanner.zip -d /opt && \
    ln -s /opt/sonar-scanner-6.2.1.4610-linux-x64/bin/sonar-scanner /usr/local/bin/sonar-scanner && \
    rm /tmp/sonar-scanner.zip

RUN usermod -aG docker jenkins

RUN jenkins-plugin-cli --plugins \
    "docker-workflow:latest \
     git:latest \
     junit:latest \
     sonar:latest \
     workflow-aggregator:latest \
     github:latest"

USER jenkins
