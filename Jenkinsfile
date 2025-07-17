pipeline {
    agent any

    environment {
      // Raporları workspace altında artifacts/reports içine toplayacağız
      REPORT_DIR = 'artifacts/reports'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t daily-rates-app:2 .'
                sh 'docker tag daily-rates-app:2 daily-rates-app:latest'
            }
        }

        stage('Test') {
            steps {
                // 1) Önce rapor klasörünü oluştur
                sh "mkdir -p ${REPORT_DIR}"
                // 2) Docker konteyner içinde pytest çalıştır, JUnit XML & HTML rapor üret
                sh """
                  docker run --rm \
                    -v \$(pwd)/${REPORT_DIR}:/app/${REPORT_DIR} \
                    daily-rates-app:2 \
                    pytest tests \\
                      --junitxml=${REPORT_DIR}/junit-results.xml \\
                      --html=${REPORT_DIR}/report.html \\
                      --self-contained-html
                """
            }
        }

        stage('Deploy') {
            steps {
                echo "🚀 Deployment adımları burada yapılacak"
                // Örneğin: sh 'kubectl apply -f k8s/deployment.yaml'
            }
        }
    }

    post {
        always {
            echo "🔔 Pipeline tamamlandı, raporlar arşivleniyor…"
        }
        success {
            echo "✅ Pipeline başarılı!"
        }
        failure {
            echo "❌ Pipeline başarısız oldu!"
        }

        // Raporları yayınlama:
        always {
            // Test sonuçlarını JUnit ile oku:
            junit "${REPORT_DIR}/junit-results.xml"

            // HTML raporu 'Reports' altında göster:
            publishHTML([
                reportName:          'Daily Rates HTML Report',
                reportDir:           "${REPORT_DIR}",
                reportFiles:         'report.html',
                keepAll:             true,
                alwaysLinkToLastBuild: true,
                allowMissing:        false
            ])
        }
    }
}
