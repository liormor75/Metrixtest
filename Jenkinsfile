pipeline {
    agent any
    environment {
        DOCKER_IMAGE = "liormor75/nginx-app"
        DOCKER_REGISTRY = "docker.io"
        DOCKER_CREDENTIALS = "docker-credentials-id"
    }
    stages {
        stage('Checkout') {
            steps {
                sh 'mkdir -p ~/.ssh && echo "StrictHostKeyChecking no" >> ~/.ssh/config'
            }
                git url: 'git@github.com:liormor75/Metrixtest.git', branch: 'main', credentialsId: 'github-ssh-key'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    def app = docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }
        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_CREDENTIALS) {
                        docker.image("${DOCKER_IMAGE}:latest").push()
                    }
                }
            }
        }
        stage('Trigger ArgoCD Sync') {
            steps {
                script {
                    build job: 'Trigger-ArgoCD-Sync', wait: false, parameters: [
                        string(name: 'IMAGE_TAG', value: "latest")
                    ]
                }
            }
        }
    }
}
