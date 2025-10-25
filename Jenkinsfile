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
          image 'vengageshbabu1605/devops_dashboard-ci:latest'
          label 'blackkey'
          reuseNode true
          // If you need to expose host ports or mount volumes, add args here, e.g.
          // args '-p 8000:8000 -v ${WORKSPACE}:/workspace'
        }
      }
      steps {
        sh '''
          set -e
          cd /workspace || cd $WORKSPACE || true

          echo "Starting FastAPI app in background (uvicorn)..."
          # start uvicorn in background; adjust module:path if your app differs
          uvicorn main:app --host 0.0.0.0 --port 8000 &
          SERVER_PID=$!

          # wait for the server to accept connections
          echo "Waiting for server to start..."
          for i in 1 2 3 4 5 6 7 8 9 10; do
            if curl -sS http://127.0.0.1:8000/ >/dev/null 2>&1; then
              echo "Server is up"
              break
            fi
            sleep 1
          done

          echo "Running smoke test on root endpoint..."
          # expect page to contain "DevOps Dashboard" — change as appropriate
          curl -sS http://127.0.0.1:8000/ | grep "DevOps Dashboard"

          echo "Stopping FastAPI app..."
          kill $SERVER_PID || true
        '''
      }
    }
  } // end stages

  post {
    success { echo 'Pipeline finished successfully.' }
    failure { echo 'Pipeline failed — check console output.' }
  }
}
