pipeline {
    agent any
    environment {
        DOCKER_CREDENTIALS_ID = 'docker-login-id'
        DOCKER_REGISTRY = 'localhost:5000'
        IMAGE_NAME = 'nginx-app'
        IMAGE_TAG = 'latest'
        ARGOCD_CREDENTIALS_ID = 'argocd-login-id'
        ARGOCD_SERVER = '127.0.0.1:8081'
        ARGOCD_APP_NAME = 'test1'
        KUBECONFIG = '/path/to/your/kubeconfig' // Ensure this points to the correct kubeconfig file
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
                    sh 'docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} .'
                }
            }
        }
        stage('Login to Docker Registry') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIALS_ID, usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh "echo \$DOCKER_PASSWORD | docker login \$DOCKER_REGISTRY -u \$DOCKER_USERNAME --password-stdin"
                    }
                }
            }
        }
        stage('Push Docker Image') {
            steps {
                script {
                    sh 'docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}'
                }
            }
        }
        stage('Update Kubernetes Deployment') {
            steps {
                script {
                    // Run kubectl set image correctly
                    sh 'kubectl set image deployment/nginx-deployment nginx=${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} --record'
                }
            }
        }
        stage('Trigger ArgoCD Sync') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: ARGOCD_CREDENTIALS_ID, usernameVariable: 'ARGOCD_USERNAME', passwordVariable: 'ARGOCD_PASSWORD')]) {
                        sh """
                            argocd login ${ARGOCD_SERVER} --username \$ARGOCD_USERNAME --password \$ARGOCD_PASSWORD --insecure
                            argocd app sync ${ARGOCD_APP_NAME}
                        """
                    }
                }
            }
        }
    }
    post {
        always {
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
