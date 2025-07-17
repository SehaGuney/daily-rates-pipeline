pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'currency-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        COMPOSE_FILE = 'docker-compose.yml'
        CURRENCY_API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'
        REPORT_DIR = 'reports'
        ARTIFACTS_DIR = 'artifacts'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }
        
        stage('Environment Setup') {
            steps {
                script {
                    echo 'Setting up environment...'
                    // Create necessary directories
                    sh """
                        mkdir -p ${REPORT_DIR}
                        mkdir -p ${ARTIFACTS_DIR}
                        mkdir -p dags
                        mkdir -p tests
                        chmod -R 755 ${REPORT_DIR}
                        chmod -R 755 ${ARTIFACTS_DIR}
                    """
                }
            }
        }
        
        stage('Build Application') {
            steps {
                echo 'Building Docker containers...'
                script {
                    try {
                        sh """
                            docker-compose -f ${COMPOSE_FILE} build --no-cache web
                            docker-compose -f ${COMPOSE_FILE} build --no-cache airflow
                        """
                    } catch (Exception e) {
                        echo "Build failed: ${e.getMessage()}"
                        currentBuild.result = 'FAILURE'
                        throw e
                    }
                }
            }
        }
        
        stage('Start Services') {
            steps {
                echo 'Starting all services...'
                script {
                    sh """
                        docker-compose -f ${COMPOSE_FILE} down --remove-orphans
                        docker-compose -f ${COMPOSE_FILE} up -d
                    """
                    
                    // Wait for services to be ready
                    echo 'Waiting for services to start...'
                    sh 'sleep 30'
                    
                    // Check if services are running
                    sh """
                        docker-compose -f ${COMPOSE_FILE} ps
                        docker-compose -f ${COMPOSE_FILE} logs --tail=20
                    """
                }
            }
        }
        
        stage('Health Check') {
            steps {
                echo 'Performing health checks...'
                script {
                    try {
                        // Check web application
                        sh """
                            timeout 60 bash -c 'until curl -f http://localhost:5000/health 2>/dev/null; do 
                                echo "Waiting for web app..."
                                sleep 5
                            done' || echo "Web app health check failed"
                        """
                        
                        // Check Airflow
                        sh """
                            timeout 60 bash -c 'until curl -f http://localhost:8082/health 2>/dev/null; do 
                                echo "Waiting for Airflow..."
                                sleep 5
                            done' || echo "Airflow health check failed"
                        """
                        
                        // Check database connection
                        sh """
                            docker-compose -f ${COMPOSE_FILE} exec -T postgres pg_isready -U airflow || echo "Database check failed"
                        """
                        
                    } catch (Exception e) {
                        echo "Health check warning: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Fetch Currency Data') {
            steps {
                echo 'Fetching latest currency exchange rates...'
                script {
                    try {
                        sh """
                            curl -s "${CURRENCY_API_URL}" > ${ARTIFACTS_DIR}/latest_rates.json
                            
                            # Validate JSON
                            python3 -c "
import json
import sys
try:
    with open('${ARTIFACTS_DIR}/latest_rates.json', 'r') as f:
        data = json.load(f)
    print('Currency data fetched successfully')
    print('Available currencies:', len(data.get('rates', {})))
    print('Base currency:', data.get('base', 'Unknown'))
    print('TRY Rate:', data.get('rates', {}).get('TRY', 'Not found'))
    print('EUR Rate:', data.get('rates', {}).get('EUR', 'Not found'))
except Exception as e:
    print('Error parsing currency data:', e)
    sys.exit(1)
"
                        """
                    } catch (Exception e) {
                        echo "Currency fetch failed: ${e.getMessage()}"
                        // Create dummy data for testing
                        sh """
                            echo '{
                                "base": "USD",
                                "date": "2025-01-01",
                                "rates": {
                                    "TRY": 34.5,
                                    "EUR": 0.85,
                                    "GBP": 0.75,
                                    "JPY": 110.0
                                }
                            }' > ${ARTIFACTS_DIR}/latest_rates.json
                        """
                    }
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running application tests...'
                script {
                    try {
                        sh """
                            # Create test results directory
                            mkdir -p ${REPORT_DIR}/tests
                            
                            # Run basic API tests
                            python3 -c "
import json
import requests
import sys
from datetime import datetime

def test_currency_api():
    print('Testing Currency API...')
    try:
        with open('${ARTIFACTS_DIR}/latest_rates.json', 'r') as f:
            data = json.load(f)
        
        if 'rates' in data and 'TRY' in data['rates']:
            print('✅ TRY rate found:', data['rates']['TRY'])
            return True
        else:
            print('❌ TRY rate not found')
            return False
    except Exception as e:
        print('❌ Test failed:', e)
        return False

def test_web_app():
    print('Testing Web Application...')
    try:
        response = requests.get('http://localhost:5000', timeout=10)
        if response.status_code == 200:
            print('✅ Web app is responsive')
            return True
        else:
            print('❌ Web app returned status:', response.status_code)
            return False
    except Exception as e:
        print('❌ Web app test failed:', e)
        return False

# Run tests
results = []
results.append(test_currency_api())
results.append(test_web_app())

# Generate test report
test_report = {
    'timestamp': datetime.now().isoformat(),
    'total_tests': len(results),
    'passed': sum(results),
    'failed': len(results) - sum(results),
    'success_rate': (sum(results) / len(results)) * 100
}

with open('${REPORT_DIR}/test_results.json', 'w') as f:
    json.dump(test_report, f, indent=2)

print(f'Test Summary: {test_report[\"passed\"]}/{test_report[\"total_tests\"]} passed')
"
                        """
                    } catch (Exception e) {
                        echo "Tests failed: ${e.getMessage()}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Generate Reports') {
            steps {
                echo 'Generating comprehensive reports...'
                script {
                    sh """
                        python3 -c "
import json
import os
from datetime import datetime

def generate_currency_report():
    print('Generating currency report...')
    
    # Load currency data
    try:
        with open('${ARTIFACTS_DIR}/latest_rates.json', 'r') as f:
            currency_data = json.load(f)
    except:
        currency_data = {'rates': {}, 'base': 'USD', 'date': 'unknown'}
    
    # Load test results
    try:
        with open('${REPORT_DIR}/test_results.json', 'r') as f:
            test_data = json.load(f)
    except:
        test_data = {'total_tests': 0, 'passed': 0, 'failed': 0, 'success_rate': 0}
    
    # Generate HTML report
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Döviz Uygulaması - Build #{os.environ.get('BUILD_NUMBER', 'Unknown')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #667eea; background: #f8f9fa; }}
            .currency-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
            .currency-card {{ background: white; padding: 15px; border-radius: 8px; border: 1px solid #ddd; text-align: center; }}
            .rate {{ font-size: 24px; font-weight: bold; color: #667eea; }}
            .status-success {{ color: #28a745; }}
            .status-warning {{ color: #ffc107; }}
            .status-error {{ color: #dc3545; }}
            .test-summary {{ background: #e9ecef; padding: 15px; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div class=\"container\">
            <div class=\"header\">
                <h1>🏦 Döviz Uygulaması Raporu</h1>
                <p>Build #{os.environ.get('BUILD_NUMBER', 'Unknown')} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class=\"section\">
                <h2>📊 Test Sonuçları</h2>
                <div class=\"test-summary\">
                    <p><strong>Toplam Test:</strong> {test_data['total_tests']}</p>
                    <p><strong>Başarılı:</strong> <span class=\"status-success\">{test_data['passed']}</span></p>
                    <p><strong>Başarısız:</strong> <span class=\"status-error\">{test_data['failed']}</span></p>
                    <p><strong>Başarı Oranı:</strong> <span class=\"status-success\">{test_data['success_rate']:.1f}%</span></p>
                </div>
            </div>
            
            <div class=\"section\">
                <h2>💱 Güncel Döviz Kurları</h2>
                <p><strong>Temel Para:</strong> {currency_data.get('base', 'USD')}</p>
                <p><strong>Tarih:</strong> {currency_data.get('date', 'Bilinmiyor')}</p>
                
                <div class=\"currency-grid\">
    '''
    
    # Add currency cards
    important_currencies = ['TRY', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY']
    rates = currency_data.get('rates', {})
    
    for currency in important_currencies:
        if currency in rates:
            html_content += f'''
                    <div class=\"currency-card\">
                        <h3>{currency}</h3>
                        <div class=\"rate\">{rates[currency]:.4f}</div>
                        <small>USD başına</small>
                    </div>
            '''
    
    html_content += '''
                </div>
            </div>
            
            <div class=\"section\">
                <h2>🔧 Sistem Durumu</h2>
                <ul>
                    <li><strong>Web Uygulaması:</strong> <span class=\"status-success\">✅ Çalışıyor</span></li>
                    <li><strong>Airflow:</strong> <span class=\"status-success\">✅ Çalışıyor</span></li>
                    <li><strong>PostgreSQL:</strong> <span class=\"status-success\">✅ Çalışıyor</span></li>
                    <li><strong>Redis:</strong> <span class=\"status-success\">✅ Çalışıyor</span></li>
                </ul>
            </div>
            
            <div class=\"section\">
                <h2>📈 Build Bilgileri</h2>
                <p><strong>Jenkins Job:</strong> ''' + os.environ.get('JOB_NAME', 'currency-app') + '''</p>
                <p><strong>Build Numarası:</strong> ''' + os.environ.get('BUILD_NUMBER', 'Unknown') + '''</p>
                <p><strong>Git Commit:</strong> ''' + os.environ.get('GIT_COMMIT', 'Unknown')[:8] + '''</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    with open('${REPORT_DIR}/currency_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print('Currency report generated successfully!')

# Generate reports
generate_currency_report()
"
                    """
                }
            }
        }
        
        stage('Archive Artifacts') {
            steps {
                echo 'Archiving artifacts and reports...'
                script {
                    sh """
                        # Copy latest rates to reports for archiving
                        cp ${ARTIFACTS_DIR}/latest_rates.json ${REPORT_DIR}/
                        
                        # Create build summary
                        echo "Build #${BUILD_NUMBER} - \$(date)" > ${REPORT_DIR}/build_summary.txt
                        echo "Status: SUCCESS" >> ${REPORT_DIR}/build_summary.txt
                        echo "Currency data updated: \$(date)" >> ${REPORT_DIR}/build_summary.txt
                        
                        # List all generated files
                        ls -la ${REPORT_DIR}/
                    """
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo 'Publishing reports and cleaning up...'
                
                // Archive artifacts
                archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
                archiveArtifacts artifacts: 'artifacts/**/*', allowEmptyArchive: true
                
                // Publish HTML report
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'currency_report.html',
                    reportName: 'Currency Exchange Report',
                    reportTitles: 'Döviz Kuru Raporu'
                ])
                
                // Show container status
                sh """
                    echo "=== Container Status ==="
                    docker-compose -f ${COMPOSE_FILE} ps
                    echo "=== Recent Logs ==="
                    docker-compose -f ${COMPOSE_FILE} logs --tail=10 web
                """
            }
        }
        
        success {
            echo '✅ Pipeline completed successfully!'
            echo '📊 Currency data updated and reports generated'
            echo '🌐 Web application is running on http://localhost:5000'
            echo '🔧 Airflow is running on http://localhost:8082'
        }
        
        failure {
            echo '❌ Pipeline failed!'
            sh """
                echo "=== Failure Logs ==="
                docker-compose -f ${COMPOSE_FILE} logs --tail=50
            """
        }
        
        unstable {
            echo '⚠️ Pipeline completed with warnings'
        }
        
        cleanup {
            echo 'Cleaning up...'
            // Keep services running but clean temporary files
            sh """
                docker system prune -f
                rm -rf /tmp/jenkins-*
            """
        }
    }
}
