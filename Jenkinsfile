// Jenkinsfile (proje kökünde)
pipeline {
  agent any

  environment {
    IMAGE_NAME = "yourdockerhubusername/daily-rates"
    TAG        = "${env.BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        git(
          url:      'https://github.com/SehaGuney/mlops-practice.git',
          branch:   'main',
          credentialsId: 'github-creds'
        )
      }
    }

    stage('Build & Push') {
      steps {
        script {
          // Docker‑in‑Docker konteynerinde docker komutlarını çalıştır
          docker.image('docker:20.10.16-dind').inside('-v /var/run/docker.sock:/var/run/docker.sock') {
            sh "docker build -t ${IMAGE_NAME}:${TAG} ."
            withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
              sh "echo $PASS | docker login -u $USER --password-stdin"
              sh "docker push ${IMAGE_NAME}:${TAG}"
            }
          }
        }
      }
    }

    stage('Deploy') {
      steps {
        // Proje kökünde docker-compose.yml dosyanızın olduğundan emin olun
        sh 'docker-compose down'
        sh 'docker-compose up -d'
      }
    }
  }

  post {
    success {
      echo "✅ Pipeline başarıyla tamamlandı: ${IMAGE_NAME}:${TAG}"
    }
    failure {
      echo "❌ Pipeline başarısız oldu."
    }
  }
}
