pipeline {
    agent any

    environment {
        IMAGE = 'daily-rates-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                // Runs pytest inside the "test" build stage; fails the build if any test fails
                sh 'docker build --target test -t ${IMAGE}:test .'
            }
        }

        stage('Build') {
            steps {
                sh 'docker build --target runtime -t ${IMAGE}:${BUILD_NUMBER} -t ${IMAGE}:latest .'
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    docker rm -f daily-rates-smoke || true
                    docker run -d --name daily-rates-smoke ${IMAGE}:${BUILD_NUMBER}
                    sleep 3
                    docker exec daily-rates-smoke python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"
                '''
            }
            post {
                always {
                    sh 'docker rm -f daily-rates-smoke || true'
                }
            }
        }
    }

    post {
        success {
            echo "Build ${BUILD_NUMBER} passed: ${IMAGE}:${BUILD_NUMBER}"
        }
        failure {
            echo "Build ${BUILD_NUMBER} failed"
        }
    }
}
