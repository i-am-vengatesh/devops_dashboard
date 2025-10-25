pipeline {
  agent { label 'blackkey' }

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
        docker { image 'vengateshbabu1605/devops_dashboard-ci:latest' }
      }
      steps {
        sh '''
          echo "Dependencies are pre-installed in the Docker image."
          echo "Build step complete. Ready for testing or deployment."
        '''
      }
    }
  }
}
