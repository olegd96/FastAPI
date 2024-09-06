/* groovylint-disable-next-line CompileStatic */
pipeline {
    agent any
    // parameters {
    //     text(name: 'PyEnvr', defaultValue: 'python3.11')
    // }
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
                    sudo cp -t . /home/oleg96d/IT/FastAPI/FastAPI/.env
                    '''
            }
        }
    }
        stage('TEST') {
            steps {
                withPythonEnv('python3.11') {
                    sh 'pytest'
            }
        }
}
    }
}
