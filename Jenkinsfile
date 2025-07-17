pipeline {
  /* Burada artık 'docker:dind' imajını kullanıyoruz;
     CLI + daemon socket’i monteli halde geliyor */
  agent {
    docker {
      image 'docker:20.10.16-dind'
      args  '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
    }
  }

  environment {
    // İstersen Docker Hub kullanıcı/adı vs. buraya
    DOCKER_IMAGE = 'myrepo/mlops-practice'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build & Push') {
      steps {
        sh "docker build -t ${DOCKER_IMAGE}:latest ."
        sh "docker push ${DOCKER_IMAGE}:latest"
      }
    }

    // Başka stage’lerin varsa buraya ekle…
  }

  post {
    success { echo '✅ Pipeline tamamlandı.' }
    failure { echo '❌ Pipeline başarısız oldu.' }
  }
}
