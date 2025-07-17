pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "daily-rates-app"
        DOCKER_TAG = "${env.BUILD_ID}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // Docker imajını build et
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                }
            }
        }
        
        stage('Test') {
            steps {
                script {
                    // Test container'ını çalıştır
                    sh """
                        docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} python -c "
                        import sys
                        print('Python version:', sys.version)
                        print('Container test passed!')
                        "
                    """
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    // Eski container'ları durdur
                    sh "docker stop daily-rates-container || true"
                    sh "docker rm daily-rates-container || true"
                    
                    // Yeni container'ı başlat
                    sh """
                        docker run -d \
                            --name daily-rates-container \
                            -p 5001:5000 \
                            ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                }
            }
        }
    }
    
    post {
        always {
            // Workspace temizleme
            script {
                try {
                    cleanWs()
                } catch (Exception e) {
                    echo "Workspace cleanup failed: ${e.getMessage()}"
                }
            }
        }
        success {
            echo "✅ Pipeline başarıyla tamamlandı!"
        }
        failure {
            echo "❌ Pipeline başarısız oldu!"
        }
    }
}