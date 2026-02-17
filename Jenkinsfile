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
        stage('Update K8s Manifest') {
            steps {
                // This targets the deployment.yaml in your repo's /k8s folder
                // It replaces the generic 'latest' or a placeholder with the specific build tag
                sh "sed -i 's|${ACR_SERVER}/${IMAGE_NAME}:latest|${ACR_SERVER}/${IMAGE_NAME}:${TAG}|g' deployment.yaml"
            }
        }
        // stage('Deploy to QA') {
        //     steps {
        //         withCredentials([usernamePassword(credentialsId: 'techtrackr-acr-push', 
        //                                         passwordVariable: 'AZURE_CLIENT_SECRET', 
        //                                         usernameVariable: 'AZURE_CLIENT_ID')]) {
        //             sh '''
        //             # login using the environment variables set by withCredentials
        //             az login --service-principal -u "$AZURE_CLIENT_ID" -p "$AZURE_CLIENT_SECRET" -t "$AZURE_TENANT_ID"
                    
        //             # Deploy to ACI
        //             az container create \
        //             --resource-group rg-tracktech-qa-001 \
        //             --name techtrackr-qa-app \
        //             --image techtrackrsea.azurecr.io/techtrackr-app:${BUILD_NUMBER} \
        //             --cpu 1 --memory 1.5 \
        //             --registry-login-server techtrackrsea.azurecr.io \
        //             --registry-username "$AZURE_CLIENT_ID" \
        //             --registry-password "$AZURE_CLIENT_SECRET" \
        //             --os-type Linux \
        //             --ports 80 \
        //             --dns-name-label techtrackr-qa-dev
        //             '''
        //         }
        //     }
        // }
    stage('Deploy to QA') {
        steps {
            // Wrap everything in one block so all variables are available at once
            withCredentials([
                usernamePassword(credentialsId: 'techtrackr-acr-push', passwordVariable: 'AZURE_CLIENT_SECRET', usernameVariable: 'AZURE_CLIENT_ID'),
                string(credentialsId: 'AZURE_LOG_WORKSPACE_KEY', variable: 'LOG_KEY'),
                string(credentialsId: 'AZURE_LOG_WORKSPACE_ID', variable: 'LOG_ID') 
            ]) {
                sh '''#!/bin/bash
                # 1. Login
                az login --service-principal -u "$AZURE_CLIENT_ID" -p "$AZURE_CLIENT_SECRET" -t "$AZURE_TENANT_ID"
                
                # 2. Deploy to ACI with BOTH Port 80 and Logging
                az container create \
                    --resource-group rg-tracktech-qa-001 \
                    --name techtrackr-qa-app \
                    --image ${ACR_SERVER}/${IMAGE_NAME}:${TAG} \
                    --cpu 1 --memory 1.5 \
                    --registry-login-server ${ACR_SERVER} \
                    --registry-username "$AZURE_CLIENT_ID" \
                    --registry-password "$AZURE_CLIENT_SECRET" \
                    --os-type Linux \
                    --ports 80 \
                    --environment-variables \
                        AZURE_CLIENT_ID="$AZURE_CLIENT_ID" \
                        AZURE_CLIENT_SECRET="$AZURE_CLIENT_SECRET" \
                        AZURE_TENANT_ID="$AZURE_TENANT_ID" \
                    --dns-name-label techtrackr-qa-dev \
                    --log-analytics-workspace "$LOG_ID" \
                    --log-analytics-workspace-key "$LOG_KEY"
                '''
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