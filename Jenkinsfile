/* groovylint-disable-next-line CompileStatic */
pipeline {
    agent any
    options {
        timestamps()
        buildDiscarder logRotator(daysToKeepStr: '3',
                                  numToKeepStr: '3')
        timeout(time: 20, unit: 'MINUTES')
    }

    parameters {
        text(name: 'PyEnvr', defaultValue: 'python3.11')
    }
    stages {
        stage('GIT') {
            steps {
                git branch: 'main', url: 'https://github.com/olegd96/FastAPI.git'
            }
        }
        stage('BUILD') {
            steps {
                withPythonEnv("${params.PyEnvr}") {
                    sh '''
                    python3 --version pip3 install poetry
                    export PATH="$HOME/.local/bin:$PATH"
                    poetry config virtualenvs.in-project true
                    poetry install
                    sudo cp -t . /home/oleg96d/IT/FastAPI/FastAPI/.env
                    '''
            }
        }
    }
        stage('TEST') {
            steps {
                withPythonEnv("${params.PyEnvr}") {
                    sh 'pytest'
            }
        }
    }
        stage('DOCKER') {
            steps {
                sh '''
                export PATH="$HOME/.local/bin:$PATH" 
                docker build . -t 127.0.0.1:32000/booking_app:registry
                docker push 127.0.0.1:32000/booking_app
                '''
                }
        }
    }
    post {
            success {
                emailext body: "Build ${currentBuild.fullDisplayName} succeeded",
                subject: "${env.JOB_NAME} - Build #${env.BUILD_NUMBER} - Successful",
                to: 'chepalin@yandex.ru',
                attachLog: true
            }
    }

}
