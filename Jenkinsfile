pipeline {
    agent any
    
    environment {
        // Define Docker Hub credentials ID that you've configured in Jenkins
        DOCKER_CREDENTIALS = credentials('docker-jenkins')
        // Your Docker Hub username
        DOCKER_USERNAME = 'saadgillani7'
        // Your Docker image name
        DOCKER_IMAGE_NAME = 'ml-app'
        // Tag with build number for versioning
        DOCKER_IMAGE_TAG = "v1.0.${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Python Dependencies') {
            steps {
                sh '''
                # (Optional) Update package lists and install python3-venv if not already installed.
                sudo apt-get update -y
                sudo apt-get install -y python3-venv

                # Create a virtual environment
                python3 -m venv venv

                # Activate the virtual environment
                . venv/bin/activate

                # Upgrade pip, setuptools (to version 68 or later), and wheel.
                pip install --upgrade pip "setuptools>=68" wheel

                # Install required packages from requirements.txt using binary wheels only.
                pip install --only-binary :all: -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                # Activate the virtual environment and run tests
                . venv/bin/activate
                PYTHONPATH=. python3 -m pytest tests/
                '''
            }
        }
        
        stage('Build Application') {
            steps {
                sh '''
                # Activate the virtual environment
                . venv/bin/activate

                # Create data directory if it doesn't exist
                mkdir -p data
                
                # Copy the dataset
                cp /home/saad/Desktop/ML-CICD-pipeline/data/WineQT.csv data/
                
                # Train the model
                python3 src/model/train.py

                # Create deployment package
                mkdir -p deployment
                mkdir -p deployment/data  # Explicitly create data directory in deployment
                cp -r src/ deployment/
                cp model.keras deployment/
                cp requirements.txt deployment/
                cp -r data/*.csv deployment/data/  # Copy only CSV files to be explicit
                
                # List files for debugging
                echo "Contents of deployment directory:"
                ls -la deployment/
                echo "Contents of deployment/data directory:"
                ls -la deployment/data/
                
                tar -czf ml-app-v1.0.${BUILD_NUMBER}.tar.gz deployment/
                '''
            }
        }
        
        stage('Dockerize Application') {
            steps {
                sh '''
                # Create a Dockerfile in the workspace
                cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY deployment/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code, model, and data
COPY deployment/src/ ./src/
COPY deployment/model.keras .
COPY deployment/data/ ./data/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=model.keras

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "src/app.py"]
EOF

                # Build the Docker image with full registry path
                docker build -t docker.io/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} .
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-jenkins', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                    echo "Logging in to Docker Hub..."
                    echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
                    
                    echo "Pushing image to Docker Hub..."
                    docker push docker.io/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}
                    
                    echo "Tagging as latest..."
                    docker tag docker.io/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} docker.io/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:latest
                    
                    echo "Pushing latest tag..."
                    docker push docker.io/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:latest
                    
                    echo "Logging out from Docker Hub..."
                    docker logout
                    '''
                }
            }
        }
        
        stage('Deploy Application') {
            steps {
                sh '''
                # Create deployment directory and copy package
                DEPLOY_DIR=/var/lib/jenkins/deployed-apps/ml-app-v1.0.${BUILD_NUMBER}
                mkdir -p $DEPLOY_DIR
                cp ml-app-v1.0.${BUILD_NUMBER}.tar.gz $DEPLOY_DIR/
                
                # Extract package for verification
                cd $DEPLOY_DIR
                tar -xzf ml-app-v1.0.${BUILD_NUMBER}.tar.gz
                
                echo "Deployed to $DEPLOY_DIR"
                
                # Create a docker-compose.yml file for easy deployment
                cat > docker-compose.yml << EOF
version: '3'
services:
  ml-app:
    image: docker.io/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}
    ports:
      - "5000:5000"
    restart: unless-stopped
EOF
                '''
            }
        }
    }
    
    post {
        success {
            echo "Build successful! ML application deployed to /var/lib/jenkins/deployed-apps/ml-app-v1.0.${BUILD_NUMBER}"
            echo "Docker image pushed to Docker Hub: docker.io/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
            emailext (
                subject: "Pipeline Success: ML Application Deployment",
                body: "ML Application has been successfully deployed.\nVersion: v1.0.${BUILD_NUMBER}\nDocker Image: docker.io/${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}",
                to: "godsu46@gmail.com"
            )
        }
        failure {
            echo "Build failed! hehe Please check the logs for details."
            emailext (
                subject: "Pipeline Failed:ML Application Deployment",
                body: "ML Application deployment failed. Please check Jenkins logs for details.",
                to: "godsu46@gmail.com"
            )
        }
    }
}