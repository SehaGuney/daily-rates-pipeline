pipeline {
  /* Docker‑in‑Docker ajanı: CLI + daemon socket’i monteli halde geliyor */
  agent {
    docker {
      image 'docker:20.10.16-dind'
      args  '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
    }
  }

  environment {
    // Docker Hub veya registry adresin
    DOCKER_IMAGE = 'myrepo/mlops-practice'
  }

  options {
    // Build cache temizleme, timeout vs. ekleyebilirsin
    timestamps()
    timeout(time: 30, unit: 'MINUTES')
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build') {
      steps {
        script {
          echo "🔨 Building Docker image ${DOCKER_IMAGE}:latest"
        }
        sh "docker build -t ${DOCKER_IMAGE}:latest ."
      }
    }

    stage('Push') {
      steps {
        script {
          echo "📤 Pushing image to registry"
        }
        withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh '''
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            docker push ${DOCKER_IMAGE}:latest
          '''
        }
      }
    }
  }

  post {
    success {
      echo '✅ Pipeline tamamlandı.'
    }
    failure {
      echo '❌ Pipeline başarısız oldu.'
    }
    always {
      // İsteğe bağlı: workspace temizle
      cleanWs()
    }
  }
}
