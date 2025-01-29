pipeline {
    agent any
    environment {
        DOCKER_CREDENTIALS_ID = 'docker-login-id'  // Replace with your actual Jenkins credentials ID
        DOCKER_REGISTRY = 'localhost:5000'
        IMAGE_NAME = 'nginx-app'
        IMAGE_TAG = 'latest'
    }
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/liormor75/Metrixtest.git', branch: 'main'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    // Build Docker image
                    sh 'docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} .'
                }
            }
        }
        stage('Login to Docker Registry') {
            steps {
                script {
                    // Use Jenkins credentials to login to Docker registry
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIALS_ID, usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh """
                            echo \$DOCKER_PASSWORD | docker login \$DOCKER_REGISTRY -u \$DOCKER_USERNAME --password-stdin
                        """
                    }
                }
            }
        }
        stage('Push Docker Image') {
            steps {
                script {
                    // Push the Docker image to local registry
                    sh 'docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}'
                }
            }
        }
        stage('Trigger ArgoCD Sync') {
            steps {
                script {
                    // Trigger ArgoCD Sync
                    echo 'Triggering ArgoCD Sync'
                    // You can add ArgoCD command here to sync your app
                    // Example: sh 'argocd app sync your-app-name'
                }
            }
        }
        stage('Post Actions') {
            steps {
                script {
                    echo 'This will always run, regardless of pipeline success or failure.'
                }
            }
        }
    }
    post {
        always {
            // Actions to run after the pipeline completes, like cleanup or notifications
            echo 'Pipeline completed.'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
