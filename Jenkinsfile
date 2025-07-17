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
                // workspace içinde rapor klasörü
                sh "mkdir -p ${env.WORKSPACE}/${REPORT_DIR}"

                // tests klasörünü de mount edip, tek satır halinde çalıştırıyoruz
                sh """
                  docker run --rm \
                    -v ${env.WORKSPACE}/${REPORT_DIR}:/app/${REPORT_DIR} \
                    -v ${env.WORKSPACE}/tests:/app/tests \
                    -w /app \
                    daily-rates-app:2 \
                    pytest tests --junitxml=${REPORT_DIR}/junit-results.xml --html=${REPORT_DIR}/report.html --self-contained-html
                """
            }
        }

        stage('Deploy') {
            steps {
                // Basitçe echo ile aşamanın çalıştığını görebiliriz
                echo "🚀 Deploy aşaması devreye girdi!"
                // gerçek deploy komutlarınızı buraya ekleyin
            }
        }
    }

    post {
        always {
            echo "🔔 Pipeline bitti, raporlar yayınlanıyor…"
            junit "${REPORT_DIR}/junit-results.xml"
            publishHTML([
                reportName:            'Daily Rates HTML Report',
                reportDir:             "${REPORT_DIR}",
                reportFiles:           'report.html',
                keepAll:               true,
                alwaysLinkToLastBuild: true,
                allowMissing:          false
            ])
        }
        success { echo "✅ Başarılı!" }
        failure { echo "❌ Başarısız!" }
    }
}
