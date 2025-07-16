pipeline {
  agent any
  stages {
    stage('Checkout') {
      steps { git 'https://github.com/SehaGuney/mlops-practice.git' }
    }
    stage('Test') {
      steps { sh 'pytest tests' }
    }
    stage('Build & Push') {
      steps {
        script {
          docker.build('youruser/daily-rates:latest')
          docker.withRegistry('', 'docker-hub-creds') {
            docker.image('youruser/daily-rates:latest').push()
          }
        }
      }
    }
    stage('Deploy') {
      steps {
        sh 'docker-compose down && docker-compose up -d'
      }
    }
  }
  post {
    success { echo '✅ Başarılı!' }
    failure { echo '❌ Hata var, kontrol et.' }
  }
}
