pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        DOCKER_HUB_USER    = "${env.DOCKER_HUB_USER}"
        DOCKER_HUB_PASS    = "${env.DOCKER_HUB_PASS}"
        IMAGE_NAME         = "${env.IMAGE_NAME ?: 'pokemon-api'}"
        NOTIFICATION_EMAIL = "${env.NOTIFICATION_EMAIL}"
        SMTP_HOST          = "${env.SMTP_HOST}"
        SMTP_PORT          = "${env.SMTP_PORT ?: '587'}"
        SMTP_USER          = "${env.SMTP_USER}"
        SMTP_PASS          = "${env.SMTP_PASS}"
    }

    stages {
        stage('Testes') {
            agent {
                docker {
                    image 'python:3.12-slim'
                    reuseNode true
                }
            }
            steps {
                sh 'pip install --quiet -r requirements.txt'
                sh '''
                    pytest src/tests \
                      --cov=app \
                      --cov-report=xml:test-results/coverage.xml \
                      --cov-report=term-missing \
                      --cov-fail-under=90 \
                      --junit-xml=test-results/junit.xml \
                      -v
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'test-results/**', allowEmptyArchive: true
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'sonar-scanner'
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build / Empacotamento') {
            steps {
                sh 'tar -czf pokemon-api-build-${BUILD_NUMBER}.tar.gz src/ requirements.txt Dockerfile'
                archiveArtifacts artifacts: "pokemon-api-build-${BUILD_NUMBER}.tar.gz"
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME}:${BUILD_NUMBER} .'
                sh 'docker tag ${DOCKER_HUB_USER}/${IMAGE_NAME}:${BUILD_NUMBER} ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest'
            }
        }

        stage('Push Docker Hub') {
            steps {
                sh 'echo "${DOCKER_HUB_PASS}" | docker login -u "${DOCKER_HUB_USER}" --password-stdin'
                sh 'docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:${BUILD_NUMBER}'
                sh 'docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest'
            }
        }
    }

    post {
        success {
            sh "bash scripts/send_email.sh SUCCESS '${env.BUILD_URL}'"
        }
        failure {
            sh "bash scripts/send_email.sh FAILURE '${env.BUILD_URL}'"
        }
    }
}
