pipeline {
    agent any
    environment {
        // Replace with your actual ACR login server (e.g., techtrackr.azurecr.io)
        ACR_SERVER = 'techtrackrsea.azurecr.io'
        IMAGE_NAME = 'techtrackr-app'
        TAG = "${env.BUILD_NUMBER}" // Uses the Jenkins build number as the version
    }
    stages {
        stage('Build Docker Image') {
            steps {
                // This builds your image using the Dockerfile in your repo
                sh "docker build -t ${ACR_SERVER}/${IMAGE_NAME}:${TAG} ."
            }
        }
        stage('Push to Azure') {
            steps {
                // This "withCredentials" block securely fetches the ID we created in Step 1
                withCredentials([usernamePassword(credentialsId: 'techtrackr-acr-push', passwordVariable: 'AZ_PASS', usernameVariable: 'AZ_USER')]) {
                    // Login to Azure Container Registry
                    sh "docker login ${ACR_SERVER} -u ${AZ_USER} -p ${AZ_PASS}"
                    // Push the image
                    sh "docker push ${ACR_SERVER}/${IMAGE_NAME}:${TAG}"
                }
            }
        }
    }
    post {
        success {
            // Cleanup: remove the local image to save disk space on your VM
            sh "docker rmi ${ACR_SERVER}/${IMAGE_NAME}:${TAG}"
        }
    }
}