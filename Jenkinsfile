pipeline {
  agent any

  environment {
    IMAGE_NAME = "yourdockerhubusername/daily-rates"
    TAG        = "${env.BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        git url: 'https://github.com/SehaGuney/mlops-practice.git', branch: 'main', credentialsId: 'github-creds'
      }
    }

    stage('Build & Push') {
      steps {
        script {
          sh "docker build -t ${IMAGE_NAME}:${TAG} ."
          withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
            sh "echo $PASS | docker login -u $USER --password-stdin"
            sh "docker push ${IMAGE_NAME}:${TAG}"
          }
        }
      }
    }

    stage('Deploy') {
      steps {
        sh 'docker-compose down'
        sh 'docker-compose up -d'
      }
    }
  }

  post {
    success {
      echo "✅ Başarılı: ${IMAGE_NAME}:${TAG}"
    }
    failure {
      echo "❌ Pipeline başarısız. Hata test adımını atlayarak build/deploy kısmına bak."  
    }
  }
}
