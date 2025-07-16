pipeline {
  agent {
    docker {
      image 'python:3.9-slim'
      args  '-v /var/run/docker.sock:/var/run/docker.sock'
    }
  }

  environment {
    IMAGE_NAME = "yourdockerhubusername/daily-rates"
    TAG        = "${env.BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout([$class: 'GitSCM',
          branches: [[name: '*/main']],
          doGenerateSubmoduleConfigurations: false,
          extensions: [],
          userRemoteConfigs: [[
            url: 'https://github.com/SehaGuney/mlops-practice.git',
            credentialsId: 'github-creds'
          ]]
        ])
      }
    }

    stage('Install & Test') {
      steps {
        sh 'pip install --upgrade pip'
        sh 'pip install -r app/requirements.txt'
        sh 'pytest tests'
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          // Docker CLI container içinde de çalışsın diye bind-mount ettik
          docker.build("${IMAGE_NAME}:${TAG}", "-f Dockerfile .")
        }
      }
    }

    stage('Push to Registry') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
          sh "echo $PASS | docker login -u $USER --password-stdin"
          sh "docker push ${IMAGE_NAME}:${TAG}"
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
      echo "✅ Pipeline tamamlandı: ${IMAGE_NAME}:${TAG}"
    }
    failure {
      echo "❌ Pipeline başarısız."
    }
  }
}
