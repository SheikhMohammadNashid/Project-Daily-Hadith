pipeline {
    agent any

    environment {
        DOCKER_USER     = "sheikhnashid"
        VM_USER         = "s0do"

        // Single production VM IP
        PROD_IP         = "192.168.0.241"

        SSH_CREDS_ID    = "vm-deploy-key"
        DOCKER_CREDS_ID = "docker-hub-creds"

        // Build tag for Docker image
        TAG             = "${env.BUILD_NUMBER}"

        // Hadith API key used by the application (injected into the container).
        // NOTE: This is provided by the user and is required for external hadith retrieval.
        HADITH_API_KEY  = '$2y$10$qqUDWLxf5jYeSOsbA49zOBUWyN88wpioiDIRwyyhAcbh5nav6arq'
    }

    options {
        timestamps()
        ansiColor('xterm')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Push') {
            steps {
                script {
                    withCredentials([
                        usernamePassword(
                            credentialsId: DOCKER_CREDS_ID,
                            usernameVariable: 'USER',
                            passwordVariable: 'PASS'
                        )
                    ]) {
                        sh 'echo $PASS | docker login -u $USER --password-stdin'

                        sh "docker build -t ${DOCKER_USER}/daily-hadith-app:v${TAG} ."
                        sh "docker tag ${DOCKER_USER}/daily-hadith-app:v${TAG} ${DOCKER_USER}/daily-hadith-app:latest"

                        sh "docker push ${DOCKER_USER}/daily-hadith-app:v${TAG}"
                        sh "docker push ${DOCKER_USER}/daily-hadith-app:latest"
                    }
                }
            }
        }

        stage('Deploy to Production') {
            steps {
                sshagent([SSH_CREDS_ID]) {
                    script {
                        echo "Deploying to Production VM..."

                        // Copy compose file
                        sh "scp -o StrictHostKeyChecking=no docker-compose.yml ${VM_USER}@${PROD_IP}:~/docker-compose.yml"

                        // Remote deployment using exported variables
                        sh """
                        ssh -o StrictHostKeyChecking=no ${VM_USER}@${PROD_IP} '
                            export TAG=${TAG}
                            export DOCKER_USER=${DOCKER_USER}
                            # Ensure the hadith API key is available to docker-compose.
                            export HADITH_API_KEY='\${HADITH_API_KEY}'

                            docker compose down || true
                            docker compose pull
                            docker compose up -d
                        '
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f || true'
        }
        failure {
            echo 'Build or deployment failed.'
        }
        success {
            echo "Deployment completed successfully for build #${env.BUILD_NUMBER}"
        }
    }
}

