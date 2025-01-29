pipeline {
    agent any
    environment {
        REGISTRY = 'localhost:5000'
        IMAGE_NAME = 'nginx-app'
        IMAGE_TAG = 'latest'
        ARGOCD_SERVER = 'argocd-server'  // Update with your ArgoCD server URL
        ARGOCD_APP_NAME = 'my-app'       // Update with your ArgoCD application name
    }
    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image
                    docker.build("${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }
        stage('Push Docker Image') {
            steps {
                script {
                    // Log in to your Docker registry (localhost)
                    sh "docker login ${REGISTRY}"
                    // Push the image to your local registry
                    sh "docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
        stage('Trigger ArgoCD Sync') {
            steps {
                script {
                    echo "Triggering ArgoCD Sync"

                    // Login to ArgoCD (adjust credentials)
                    sh """
                    argocd login ${ARGOCD_SERVER} --username admin --password 5uI43-Ig8qr3nmty --insecure
                    """

                    // Sync the ArgoCD application
                    sh "argocd app sync ${ARGOCD_APP_NAME} --revision ${IMAGE_TAG}"
                }
            }
        }
        stage('Post Actions') {
            steps {
                echo "This will always run, regardless of pipeline success or failure."
            }
        }
    }
}
