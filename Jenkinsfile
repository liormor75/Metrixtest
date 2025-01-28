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
        DOCKER_IMAGE = "nginx-hello-world"
        ARGOCD_SERVER = "127.0.0.1:8081"  // Replace with your ArgoCD server
        ARGOCD_PASSWORD = "<ARGOCD_PASSWORD>"
        ARGOCD_APP_NAME = "nginx-hello-world"
        ARGOCD_PROJECT = "default"  // Change this to your ArgoCD project if applicable
    }
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/liormor75/Metrixtest.git'  // Use your repo URL
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
                    docker.withRegistry('your-docker-registry-url', 'docker-credentials-id') {
                        docker.image(DOCKER_IMAGE).push()
                    }
                }
            }
        }
        stage('Trigger ArgoCD Sync') {
            steps {
                script {
                    sh """
                        # Log in to ArgoCD
                        argocd login ${ARGOCD_SERVER} --username admin --password ${ARGOCD_PASSWORD} --insecure
                        # Sync the app in ArgoCD
                        argocd app sync ${ARGOCD_APP_NAME}
                    """
                }
            }
        }
    }
}
