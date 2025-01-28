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
                git url: 'https://github.com/liormor75/nginx-hello-world.git', branch: 'main'
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
    }
}
stage('Trigger ArgoCD Sync') {
    steps {
        script {
            sh """
                argocd login 127.0.0.1:8081 --username admin --password 5uI43-Ig8qr3nmty --insecure
                argocd app sync nginx-app
            """
        }
    }
}
