/* groovylint-disable-next-line CompileStatic */
properties([
  parameters([
    choice(
      name: 'PyEnvr',
      description: 'Choose Python version',
      choices: ["python2.7", "python3.6", "python3.7", "python3.8", "python3.9", "python3.10", "python3.11"].join("\n")
    )
  ])
])

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
                withPythonEnv(${params.PyEnvr}) {
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
                withPythonEnv(${params.PyEnvr}) {
                    sh 'pytest'
            }
        }
}
    }
}
