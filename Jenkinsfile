pipeline {
    agent any
    stages {
        stage('GIT') {
            steps {
                git branch: 'main', url: 'https://github.com/olegd96/FastAPI.git'
            }
        }
        stage('BUILD') {
            steps {
                withPythonEnv('python3.11') {
                    sh '''python3 --version pip3 install poetry
                    export PATH="$HOME/.local/bin:$PATH"
                    poetry config virtualenvs.in-project true
                    poetry install
                    poetry shell
                    
                    '''
                }
            }
        }
        stage('TEST') {
            steps {
                withPythonEnv('python3.11') {
                    sh '''export PATH="$HOME/.local/bin:$PATH"
                    pytest'''
                }
            }
        }
    }
}
