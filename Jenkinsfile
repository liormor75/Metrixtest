pipeline {
    agent any
    environment {
        DOCKER_CREDENTIALS_ID = 'docker-login-id'  // Replace with your actual Jenkins credentials ID for Docker login
        DOCKER_REGISTRY = 'localhost:5000'
        IMAGE_NAME = 'nginx-app'
        IMAGE_TAG = 'latest'
        ARGOCD_CREDENTIALS_ID = 'argocd-login-id'  // Replace with your actual Jenkins credentials ID for ArgoCD login
        ARGOCD_SERVER = '127.0.0.1:8081'   // Replace with your actual ArgoCD server address
        ARGOCD_APP_NAME = 'test1'           // Replace with your actual ArgoCD application name
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
                    echo "Building Docker image ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}..."
                    sh 'docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} .'
                }
            }
        }
        stage('Login to Docker Registry') {
            steps {
                script {
                    // Use Jenkins credentials to login to Docker registry
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIALS_ID, usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        echo "Logging in to Docker registry ${DOCKER_REGISTRY}..."
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
                    // Push the Docker image to the local registry
                    echo "Pushing Docker image ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}..."
                    sh 'docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}'
                }
            }
        }
        stage('Update Kubernetes Deployment') {
            steps {
                script {
                    // Ensure Kubernetes deployment YAML uses the latest image
                    echo "Updating Kubernetes deployment with new Docker image ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}..."
                    sh 'kubectl set image deployment/nginx-deployment nginx=${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} --record'
                }
            }
        }
        stage('Trigger ArgoCD Sync') {
            steps {
                script {
                    // Trigger ArgoCD sync to apply the changes
                    echo "Triggering ArgoCD sync for application ${ARGOCD_APP_NAME}..."
                    withCredentials([usernamePassword(credentialsId: ARGOCD_CREDENTIALS_ID, usernameVariable: 'ARGOCD_USERNAME', passwordVariable: 'ARGOCD_PASSWORD')]) {
                        sh """
                            argocd login ${ARGOCD_SERVER} --username \$ARGOCD_USERNAME --password \$ARGOCD_PASSWORD --insecure
                            argocd app sync ${ARGOCD_APP_NAME}  // This will ensure ArgoCD syncs the updated configuration
                        """
                    }
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

