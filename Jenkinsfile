pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t daily-rates-app:2 .'
                    sh 'docker tag daily-rates-app:2 daily-rates-app:latest'
                }
            }
        }
        
        stage('Test') {
            steps {
                script {
                    sh 'docker run --rm daily-rates-app:2 python -c "import sys; print(\'Python version:\', sys.version); print(\'Container test passed!\')"'
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    echo "Deployment işlemleri burada yapılacak"
                    // Deployment komutlarınızı buraya ekleyin
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "Pipeline tamamlandı"
            }
        }
        success {
            echo "✅ Pipeline başarılı!"
        }
        failure {
            echo "❌ Pipeline başarısız oldu!"
        }
    }
}
