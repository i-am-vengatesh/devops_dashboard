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
        docker {
          image 'vengateshbabu1605/devops_dashboard-ci:latest'
          label 'blackkey'
          reuseNode true
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
     docker {
          image 'vengateshbabu1605/devops_dashboard-ci:latest'
          label 'blackkey'
          reuseNode true
          // If you need to expose host ports or mount volumes, add args here, e.g.
          // args '-p 8000:8000 -v ${WORKSPACE}:/workspace'
        }
  }
  steps {
    sh '''
      set -e
      echo "Starting FastAPI app in background..."
      uvicorn main:app --host 0.0.0.0 --port 8000 &
      SERVER_PID=$!

      echo "Waiting for server to start..."
      sleep 5

      echo "Running smoke test using httpx..."
      python smoke_test.py

      echo "Stopping FastAPI app..."
      kill $SERVER_PID
    '''
  }
}

  stage('Unit Testing (pytest)') {
  agent {
    docker {
          image 'vengateshbabu1605/devops_dashboard-ci:latest'
          label 'blackkey'
          reuseNode true
          // If you need to expose host ports or mount volumes, add args here, e.g.
          // args '-p 8000:8000 -v ${WORKSPACE}:/workspace'
        }
  }
  steps {
    sh '''
      set -e
      mkdir -p reports/tests
      pytest tests \
        --junitxml=reports/tests/test-results.xml \
        --cov=. \
        --cov-report=xml:reports/tests/coverage.xml
    '''
    stash includes: 'reports/tests/**', name: 'test-reports'
  }
}

    
stage('Archive Test Reports') {
  steps {
    unstash 'test-reports'
    junit 'reports/tests/test-results.xml'
    archiveArtifacts artifacts: 'reports/tests/coverage.xml'
  }
}

  } // end stages

  post {
    success { echo 'Pipeline finished successfully.' }
    failure { echo 'Pipeline failed — check console output.' }
  }
}
