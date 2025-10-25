pipeline {
  agent { label 'blackkey' } // or use 'any' if you don't have specific labels

  stages {
    stage('Checkout DevOps Dashboard Repo') {
      steps {
        git branch: 'main',
            url: 'https://github.com/i-am-vengatesh/devops_dashboard.git', // replace with your actual repo URL
            credentialsId: 'git-creds' // your Jenkins Git credentials ID
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
          pip install -r requirements.txt

          echo "Build step complete. (No actual build command for FastAPI app)"
        '''
      }
    }
``
    
  }
}
