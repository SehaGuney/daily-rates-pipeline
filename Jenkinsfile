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
                    // Container testi
                    sh 'docker run --rm daily-rates-app:2 python -c "import sys; print(\'Python version:\', sys.version); print(\'Container test passed!\')"'

                    // pytest ile rapor üret
                    sh '''
                        mkdir -p reports
                        pytest tests \
                          --junitxml=reports/junit-results.xml \
                          --html=reports/report.html \
                          --self-contained-html
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
            // JUnit sonuçlarını arşivle (opsiyonel)
            junit 'reports/junit-results.xml'

            // HTML raporu ekle, allowMissing eklendi
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
