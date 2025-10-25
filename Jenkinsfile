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
      export PYTHONPATH=.
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

   stage('SonarQube Analysis') {
  agent {
    docker {
      image 'vengateshbabu1605/sonar-scanner-node:latest'
      label 'blackkey'
      reuseNode true
    }
  }
  environment {
    SONAR_TOKEN = credentials('sonar-token1')
  }
  steps {
    sh '''
      sonar-scanner \
        -Dsonar.projectKey=devops_dashboard \
        -Dsonar.sources=. \
        -Dsonar.host.url=http://10.244.192.41:9000 \
        -Dsonar.token=$SONAR_TOKEN \
        -Dsonar.python.coverage.reportPaths=reports/tests/coverage.xml
    '''
  }
}

stage('Docker Build & Push') {
  agent {
    docker {
      image 'docker:latest'
      args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
    }
  }
  environment {
    DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
  }
  steps {
    sh '''
      echo "Logging in to Docker Hub..."
      echo "$DOCKERHUB_CREDENTIALS_PSW" | docker login -u "$DOCKERHUB_CREDENTIALS_USR" --password-stdin

      echo "Building Docker image..."
      docker build -t vengateshbabu1605/devops_desktop-ci:latest .

      echo "Pushing Docker image to Docker Hub..."
      docker push vengateshbabu1605/devops_desktop-ci:latest

      echo "Docker build and push completed."
    '''
  }
}

  } // end stages

  post {
    success { echo 'Pipeline finished successfully.' }
    failure { echo 'Pipeline failed — check console output.' }
  }
}
