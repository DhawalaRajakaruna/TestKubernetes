pipeline {
    agent any

    environment {
        // Docker image configuration
        DOCKER_REGISTRY = "dhawala0827"
        APP_IMAGE_NAME = "testkube_app"
        IMAGE_TAG = "${BUILD_NUMBER}"
        
        // Kubernetes configuration
        NAMESPACE = "testspace"
        DB_RELEASE = "db-release"
        APP_RELEASE = "app-release"
        HELM_CHART_PATH = "./testdir"
        
        // Minikube docker environment
        USE_MINIKUBE_DOCKER = "true"
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
                // echo "Checking out code from repository..."
                // git branch: 'main',
                //     url: 'https://github.com/DhawalaRajakaruna/TestKubernetes.git'
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    echo "Setting up environment..."
                    if (env.USE_MINIKUBE_DOCKER == 'true') {
                        sh '''
                        echo "Configuring Docker to use Minikube's Docker daemon..."
                        eval $(minikube docker-env)
                        '''
                    }
                }
            }
        }

        // stage('Run Tests') {
        //     steps {
        //         echo "Running application tests..."
        //         sh '''
        //         # Create virtual environment and run tests
        //         if [ ! -d "env" ]; then
        //             python3 -m venv env
        //         fi
        //         source env/bin/activate
        //         pip install -r requirements.txt
                
        //         # Add your test commands here
        //         # python -m pytest tests/
        //         # python -m unittest discover
                
        //         echo "Tests completed successfully"
        //         '''
        //     }
        // }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                script {
                    if (env.USE_MINIKUBE_DOCKER == 'true') {
                        sh '''
                        eval $(minikube docker-env)
                        docker build -t ${APP_IMAGE_NAME}:${IMAGE_TAG} .
                        docker tag ${APP_IMAGE_NAME}:${IMAGE_TAG} ${APP_IMAGE_NAME}:latest
                        echo "Image built in Minikube Docker daemon"
                        '''
                    } else {
                        sh '''
                        docker build -t ${DOCKER_REGISTRY}/${APP_IMAGE_NAME}:${IMAGE_TAG} .
                        docker tag ${DOCKER_REGISTRY}/${APP_IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_REGISTRY}/${APP_IMAGE_NAME}:latest
                        '''
                    }
                }
            }
        }

        stage('Push Docker Image') {
            when {
                expression { env.USE_MINIKUBE_DOCKER != 'true' }
            }
            steps {
                echo "Pushing Docker image to registry..."
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    docker push ${DOCKER_REGISTRY}/${APP_IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${DOCKER_REGISTRY}/${APP_IMAGE_NAME}:latest
                    docker logout
                    '''
                }
            }
        }

        stage('Deploy Database') {
            steps {
                echo "Deploying PostgreSQL database using Helm..."
                sh '''
                # Check if database release exists
                if helm list -n ${NAMESPACE} | grep -q ${DB_RELEASE}; then
                    echo "Upgrading existing database release..."
                    helm upgrade ${DB_RELEASE} ${HELM_CHART_PATH} \
                        -f ${HELM_CHART_PATH}/values-db.yaml \
                        -n ${NAMESPACE}
                else
                    echo "Installing new database release..."
                    helm install ${DB_RELEASE} ${HELM_CHART_PATH} \
                        -f ${HELM_CHART_PATH}/values-db.yaml \
                        -n ${NAMESPACE} \
                        --create-namespace
                fi
                
                # Wait for database to be ready
                echo "Waiting for database pod to be ready..."
                kubectl wait --for=condition=ready pod \
                    -l app=postgres \
                    -n ${NAMESPACE} \
                    --timeout=300s
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                echo "Deploying application using Helm..."
                script {
                    if (env.USE_MINIKUBE_DOCKER == 'true') {
                        sh '''
                        # Update values-app.yaml with new image tag
                        sed -i "s|image: testkube_app:.*|image: ${APP_IMAGE_NAME}:${IMAGE_TAG}|g" ${HELM_CHART_PATH}/values-app.yaml
                        
                        # Deploy or upgrade application
                        if helm list -n ${NAMESPACE} | grep -q ${APP_RELEASE}; then
                            echo "Upgrading existing application release..."
                            helm upgrade ${APP_RELEASE} ${HELM_CHART_PATH} \
                                -f ${HELM_CHART_PATH}/values-app.yaml \
                                -n ${NAMESPACE}
                        else
                            echo "Installing new application release..."
                            helm install ${APP_RELEASE} ${HELM_CHART_PATH} \
                                -f ${HELM_CHART_PATH}/values-app.yaml \
                                -n ${NAMESPACE}
                        fi
                        '''
                    } else {
                        sh '''
                        # Deploy with registry image
                        helm upgrade --install ${APP_RELEASE} ${HELM_CHART_PATH} \
                            -f ${HELM_CHART_PATH}/values-app.yaml \
                            -n ${NAMESPACE} \
                            --set app.deployment.container.image=${DOCKER_REGISTRY}/${APP_IMAGE_NAME}:${IMAGE_TAG} \
                            --set app.deployment.container.imagePullPolicy=Always
                        '''
                    }
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                echo "Verifying deployment..."
                sh '''
                # Wait for application pods to be ready
                echo "Waiting for application pods to be ready..."
                kubectl wait --for=condition=ready pod \
                    -l app=testkube \
                    -n ${NAMESPACE} \
                    --timeout=300s
                
                # Get deployment status
                echo "Application Deployment Status:"
                kubectl get deployments -n ${NAMESPACE}
                
                echo "Application Pods:"
                kubectl get pods -n ${NAMESPACE}
                
                echo "Application Services:"
                kubectl get services -n ${NAMESPACE}
                
                # Get application URL
                echo "Application URL:"
                minikube service app-service -n ${NAMESPACE} --url || echo "Service not accessible"
                '''
            }
        }

        stage('Run Health Check') {
            steps {
                echo "Running health checks..."
                sh '''
                # Get service URL
                SERVICE_URL=$(minikube service app-service -n ${NAMESPACE} --url | head -n 1)
                
                if [ -n "$SERVICE_URL" ]; then
                    echo "Testing application at: $SERVICE_URL"
                    
                    # Wait for app to be fully ready
                    sleep 10
                    
                    # Test health endpoint
                    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${SERVICE_URL}/ || echo "000")
                    
                    if [ "$HTTP_STATUS" = "200" ]; then
                        echo " Health check passed - HTTP ${HTTP_STATUS}"
                    else
                        echo "  Health check returned HTTP ${HTTP_STATUS}"
                    fi
                else
                    echo "  Could not get service URL"
                fi
                '''
            }
        }
    }

    post {
        success {
            echo "======================================"
            echo " DEPLOYMENT COMPLETED SUCCESSFULLY"
            echo "======================================"
            sh '''
            echo "Deployed Resources:"
            kubectl get all -n ${NAMESPACE}
            
            echo ""
            echo "Access the application:"
            minikube service app-service -n ${NAMESPACE} --url || true
            '''
        }
        failure {
            echo "======================================"
            echo " DEPLOYMENT FAILED"
            echo "======================================"
            sh '''
            echo "Checking pod status:"
            kubectl get pods -n ${NAMESPACE} || true
            
            echo ""
            echo "Recent pod logs:"
            kubectl logs -n ${NAMESPACE} -l app=testkube --tail=50 || true
            kubectl logs -n ${NAMESPACE} -l app=postgres --tail=50 || true
            '''
        }
        always {
            echo "Cleaning up..."
            sh '''
            # Clean up old docker images (keep last 5)
            if [ "${USE_MINIKUBE_DOCKER}" = "true" ]; then
                eval $(minikube docker-env)
                docker images | grep ${APP_IMAGE_NAME} | tail -n +6 | awk '{print $3}' | xargs -r docker rmi || true
            fi
            '''
        }
    }
}

