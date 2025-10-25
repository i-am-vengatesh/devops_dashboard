pipeline {
  agent { label 'blackkey' } // Use your Jenkins agent label

  stages {
    stage('Checkout DevOps Dashboard Repo') {
      steps {
        git branch: 'main',
            url: 'https://github.com/i-am-vengatesh/devops_dashboard.git',
            credentialsId: 'git-creds'
      }
    }

    stage('Verify Checkout') {
      steps {
        sh 'echo "Repo cloned successfully at $(pwd)"'
        sh 'ls -la'
      }
    }

    stage('Install Dependencies / Build (Docker)') {
      
    agent {
        docker { image 'python:3.11-slim' }
      }
      steps {
        sh '''
          set -e
          echo "Installing dependencies..."
          pip install --upgrade pip
          pip install --no-cache-dir --disable-pip-version-check --root-user-action=ignore -r requirements.txt

          echo "Build step complete. (No actual build command for FastAPI app)"
        '''
      }

    }
  }
}
