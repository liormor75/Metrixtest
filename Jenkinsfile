pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/liormor75/Metrixtest.git', branch: 'main'
            }
        }
    }
}
pipeline {
    agent any
    environment {
        DOCKER_IMAGE = "liormor75/nginx-app"
        DOCKER_REGISTRY = "docker.io"
        DOCKER_CREDENTIALS = "docker-credentials-id"
        ARGOCD_SERVER = "127.0.0.1:8081"  // Replace with actual ArgoCD server if needed
        ARGOCD_APP_NAME = "my-nginx-app"  // Replace with your actual ArgoCD app name
    }
    stages {
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
                    echo 'Logging into ArgoCD...'
                    sh """
                        argocd login ${ARGOCD_SERVER} --username admin --password 5uI43-Ig8qr3nmty --insecure
                        echo 'Syncing application in ArgoCD...'
                        argocd app sync ${ARGOCD_APP_NAME}
                    """
                }
            }
        }
    }
}
