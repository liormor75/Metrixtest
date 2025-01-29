pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = "localhost:5000"
        IMAGE_NAME = "nginx-app"
        GIT_REPO = "https://github.com/liormor75/Metrixtest.git"  // Replace with your actual Git repo URL
    }

    stages {
        stage('Checkout Code') {
            steps {
                script {
                    // Checkout code from the Git repository
                    git url: "${GIT_REPO}", branch: "main"  // Adjust the branch if needed
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image
                    sh "docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest ."
                }
            }
        }
        
        stage('Push Docker Image') {
            steps {
                script {
                    // Push the Docker image to the local registry
                    sh "docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"
                }
            }
        }

        stage('Trigger ArgoCD Sync') {
            steps {
                script {
                    // Add your ArgoCD sync logic here
                    echo "Triggering ArgoCD Sync"
                }
            }
        }
    }

    post {
        always {
            script {
                // This block is executed regardless of success or failure
                // You can add cleanup actions, notifications, etc.
                echo 'This will always run, regardless of pipeline success or failure.'
            }
        }
    }
}
