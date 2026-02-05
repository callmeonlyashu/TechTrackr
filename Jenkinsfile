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
        stage('Deploy to QA') {
            steps {
                // Use the standard usernamePassword binding
                withCredentials([usernamePassword(credentialsId: 'techtrackr-azure-sp', 
                                                passwordVariable: 'AZURE_CLIENT_SECRET', 
                                                usernameVariable: 'AZURE_CLIENT_ID')]) {
                    sh '''
                    # Login using the bound variables + your Tenant ID (you can hardcode Tenant ID for now)
                    az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET -t <YOUR_TENANT_ID>
                    
                    # Deploy to ACI
                    az container create \
                    --resource-group rg-tracktech-qa-001 \
                    --name techtrackr-qa-app \
                    --image techtrackrsea.azurecr.io/techtrackr-app:${BUILD_NUMBER} \
                    --cpu 1 --memory 1.5 \
                    --registry-login-server techtrackrsea.azurecr.io \
                    --registry-username $AZURE_CLIENT_ID \
                    --registry-password $AZURE_CLIENT_SECRET \
                    --os-type Linux \
                    --ports 80 \
                    --dns-name-label techtrackr-qa-dev
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