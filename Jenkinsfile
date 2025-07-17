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
                    // 1) Container içinde basit doğrulama
                    sh 'docker run --rm daily-rates-app:2 python -c "import sys; print(\'Python version:\', sys.version); print(\'Container test passed!\')"'

                    // 2) pytest ile HTML rapor üretimi
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
                    // Deployment komutlarınızı buraya ekleyin
                }
            }
        }
    }

    post {
        always {
            // Opsiyonel: JUnit test sonuçlarını de arşivle
            junit 'reports/junit-results.xml'

            // HTML raporu Jenkins’e "Küçük Rapor" sekmesi olarak ekle
            publishHTML([
                reportDir             : 'reports',
                reportFiles           : 'report.html',
                reportName            : 'Küçük Rapor',
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

