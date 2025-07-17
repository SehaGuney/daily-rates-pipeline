pipeline {
    agent any

    environment {
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
                // Rapor klasörünü oluştur
                sh "mkdir -p ${REPORT_DIR}"

                // Container içinde pytest çalıştır, raporları REPORT_DIR içine yaz
                sh """
                  docker run --rm \
                    -v "${env.WORKSPACE}/${REPORT_DIR}:/app/${REPORT_DIR}" \
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
                echo "🚀 Deployment adımları burada"
                // sh 'kubectl apply -f k8s/…'
            }
        }
    }

    post {
        always {
            echo "🔔 Pipeline tamamlandı, raporlar arşivleniyor…"

            // JUnit test raporunu oku
            junit "${REPORT_DIR}/junit-results.xml"

            // HTML raporu göster
            publishHTML([
                reportName:             'Daily Rates HTML Report',
                reportDir:              "${REPORT_DIR}",
                reportFiles:            'report.html',
                keepAll:                true,
                alwaysLinkToLastBuild:  true,
                allowMissing:           false
            ])
        }
        success {
            echo "✅ Pipeline başarılı!"
        }
        failure {
            echo "❌ Pipeline başarısız oldu!"
        }
    }
}
