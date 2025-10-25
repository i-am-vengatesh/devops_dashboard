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
      agent { node { label 'blackkey' } }
       docker { image 'vengateshbabu1605/devops_dashboard-ci:latest'}
      
    }
        
      }
      steps {
        sh '''
          echo "Dependencies are pre-installed in the Docker image."
          echo "Build step complete. Ready for testing or deployment."
        '''
      }
    }
    stage('Run & Smoke Test App') {
      agent {
        docker { image 'vengateshbabu1605/devops_dashboard-ci:latest' }
        label 'blackkey'
      }
      steps {
        sh '''
          set -e
          echo "Starting FastAPI app in background..."
          uvicorn main:app --host 0.0.0.0 --port 8000 &
          SERVER_PID=$!

          echo "Waiting for server to start..."
          sleep 5

          echo "Running smoke test on root endpoint..."
          curl -s http://localhost:8000 | grep "DevOps Dashboard"

          echo "Stopping FastAPI app..."
          kill $SERVER_PID
        '''
      }
    }
  }
}
