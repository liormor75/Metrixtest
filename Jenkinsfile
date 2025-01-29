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
                git url: 'https://github.com/liormor75/nginx-ingress.yaml', branch: 'main'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build(DOCKER_IMAGE)
                }
            }
        }
        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-credentials-id') {
                        docker.image(DOCKER_IMAGE).push()
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


