// Jenkinsfile
pipeline {
  agent any

  stages {
    stage('Build') {
      steps {
        sh 'docker build -t my-app:latest .'
      }
    }

    stage('Test') {
      steps {
        sh '''
          mkdir -p artifacts/reports
          pytest tests \
            --junitxml=artifacts/reports/junit-results.xml \
            --html=artifacts/reports/report.html \
            --self-contained-html
        '''
      }
    }
  }

  post {
    always {
      junit 'artifacts/reports/junit-results.xml'
      publishHTML([
        reportName: 'My HTML Report',
        reportDir: 'artifacts/reports',
        reportFiles: 'report.html',
        keepAll: true,
        alwaysLinkToLastBuild: true,
        allowMissing: false
      ])
    }
  }
}
