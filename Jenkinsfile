pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t daily-rates-app:2 .'
                    sh 'docker tag daily-rates-app:2 daily-rates-app:latest'
                }
            }
        }

        stage('Test & Generate Report') {
            steps {
                script {
                    // 1) Container testi
                    sh 'docker run --rm daily-rates-app:2 python -c "import sys; print(\'Python version:\', sys.version); print(\'Container test passed!\')"'

                    // 2) pytest + HTML rapor => container içinde pip yükle, volume ile host'a al
                    sh '''
                        mkdir -p ${WORKSPACE}/reports
                        docker run --rm \
                          -v "${WORKSPACE}/reports":/app/reports \
                          daily-rates-app:2 bash -c "pip install pytest pytest-html && pytest tests \
                            --junitxml=/app/reports/junit-results.xml \
                            --html=/app/reports/report.html \
                            --self-contained-html"
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo "Deployment işlemleri burada yapılacak"
                    // Buraya deploy komutlarını ekle
                }
            }
        }
    }

    post {
        always {
            // JUnit sonuçlarını arşivle
            junit 'reports/junit-results.xml'

            // HTML raporu ekle
            publishHTML([
                reportDir             : 'reports',
                reportFiles           : 'report.html',
                reportName            : 'Küçük Rapor',
                allowMissing          : true,
                keepAll               : false,
                alwaysLinkToLastBuild : true
            ])

            echo "Pipeline tamamlandı"
        }
        success {
            echo "✅ Pipeline başarılı!"
        }
        failure {
            echo "❌ Pipeline başarısız oldu!"
        }
    }
}
