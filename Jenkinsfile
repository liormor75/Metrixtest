pipeline {
    agent any
    
    // Define environment variables for use throughout the pipeline
    environment {
        KUBECONFIG = '/home/adminlior/config'  // Path to the kubeconfig file, it will be replaced by Jenkins credentials
        DOCKER_CREDENTIALS_ID = 'docker-login-id'  // Replace with your actual Docker login credentials ID
        DOCKER_REGISTRY = 'localhost:5000'
        IMAGE_NAME = 'nginx-app'
        IMAGE_TAG = 'latest'
        ARGOCD_CREDENTIALS_ID = 'argocd-login-id'  // Replace with your actual ArgoCD login credentials ID
        ARGOCD_SERVER = '127.0.0.1:8081'  // Replace with your actual ArgoCD server address
        ARGOCD_APP_NAME = 'test1'  // Replace with your actual ArgoCD application name
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout the code from the repository
                git url: 'https://github.com/liormor75/Metrixtest.git', branch: 'main'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image
                    sh 'docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} .'
                }
            }
        }

        stage('Login to Docker Registry') {
            steps {
                script {
                    // Login to Docker Registry using stored credentials
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
                    // Push the Docker image to the registry
                    sh 'docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}'
                }
            }
        }

        stage('Set Kubernetes Context') {
            steps {
                script {
                    // Use the kubeconfig file stored in Jenkins to set the Kubernetes context
                    withCredentials([file(credentialsId: 'my-kubeconfig', variable: 'KUBECONFIG')]) {
                        // Set the context to the correct namespace
                        sh 'kubectl config set-context --current --namespace=your-namespace'
                    }
                }
            }
        }

        stage('Update Kubernetes Deployment') {
            steps {
                script {
                    // Update the Kubernetes deployment to use the new Docker image
                    sh 'kubectl set image deployment/nginx-deployment nginx=localhost:5000/nginx-app:latest --record'
                }
            }
        }

        stage('Trigger ArgoCD Sync') {
            steps {
                script {
                    // Trigger ArgoCD Sync to deploy the new changes
                    echo 'Triggering ArgoCD Sync'
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
            // Actions to run after the pipeline completes, such as cleanup or notifications
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
