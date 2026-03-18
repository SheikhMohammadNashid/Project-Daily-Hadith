pipeline {
    agent any
    environment {
        DOCKER_USER = "sheikhnashid"
        STG_USER = "stg"
        PROD_USER = "prod"
        STAGING_IP = "192.168.1.179"
        PROD_IP = "192.168.1.161"
        DOCKER_CREDS_ID = "docker-hub-creds"
        SSH_CREDS_ID = "vm-deploy-key"
        TAG = "${env.BUILD_NUMBER}"
    }
    stages {
        stage('Build & Push') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDS_ID, passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                        sh "echo \$PASS | docker login -u \$USER --password-stdin"

                        // 1. Build & Push Backend (One image for both envs)
                        sh "docker build -t ${DOCKER_USER}/hero-backend:v${TAG} ./app"
                        sh "docker push ${DOCKER_USER}/hero-backend:v${TAG}"

                        // 2. Build & Push Frontend for STAGING (Points to .36)
                        sh "docker build --build-arg REACT_APP_API_URL=http://${STAGING_IP}:8000 -t ${DOCKER_USER}/hero-frontend:stg-v${TAG} ./Frontend"
                        sh "docker push ${DOCKER_USER}/hero-frontend:stg-v${TAG}"

                        // 3. Build & Push Frontend for PRODUCTION (Points to .35)
                        sh "docker build --build-arg REACT_APP_API_URL=http://${PROD_IP}:8000 -t ${DOCKER_USER}/hero-frontend:prod-v${TAG} ./Frontend"
                        sh "docker push ${DOCKER_USER}/hero-frontend:prod-v${TAG}"
                    }
                }
            }
        }
        stage('Deploy to Staging') {
            steps {
                sshagent([SSH_CREDS_ID]) {
                    sh "scp -o StrictHostKeyChecking=no docker-compose.staging.yml ${STG_USER}@${STAGING_IP}:~/docker-compose.yml"
                    sh """
                        ssh -o StrictHostKeyChecking=no ${STG_USER}@${STAGING_IP} '
                            docker ps -a --format "{{.Names}}" | grep -E "^(verjenkins|herovault|hero)-" | xargs -r docker rm -f
                            export TAG=${TAG}
                            export DOCKER_USER=${DOCKER_USER}
                            docker compose up -d
                        '
                    """
                }
            }
        }
        stage('Approval Gate') {
            steps {
                input message: "Verify Staging at http://${STAGING_IP}:3000. Promote to Production?", ok: "Deploy!"
            }
        }
        stage('Deploy to Production') {
            steps {
                sshagent([SSH_CREDS_ID]) {
                    sh "scp -o StrictHostKeyChecking=no docker-compose.prod.yml ${PROD_USER}@${PROD_IP}:~/docker-compose.yml"
                    sh """
                        ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_IP} '
                            docker ps -a --format "{{.Names}}" | grep -E "^(verjenkins|herovault|hero)-" | xargs -r docker rm -f
                            export TAG=${TAG}
                            export DOCKER_USER=${DOCKER_USER}
                            docker compose pull
                            docker compose up -d
                        '
                    """
                }
            }
        }
    }
}
