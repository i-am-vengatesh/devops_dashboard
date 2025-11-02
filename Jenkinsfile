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
          label 'bkps-build-1'
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
          image 'docker:24.0.2'
          label 'blackkey'
          reuseNode true
          args '--privileged -v /var/run/docker.sock:/var/run/docker.sock -u 0:0'
        }
      }
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) {
          sh '''
            echo "Logging in to Docker Hub..."
            mkdir -p /tmp/.docker
            export DOCKER_CONFIG=/tmp/.docker
            echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin

            echo "Building Docker image..."
            docker build -f Dockerfile.ci -t vengateshbabu1605/devops_desktop-ci:latest .

            echo "Pushing Docker image to Docker Hub..."
            docker push vengateshbabu1605/devops_desktop-ci:latest

            echo "Docker build and push completed."
          '''
        }
      }
    }

    // ----------------- NEW STAGE: Deploy to Kind -----------------
    stage('Deploy to Kind') {
      agent {
        docker {
          image 'bitnami/kubectl:1.29.6' // kubectl image
          label 'blackkey'
          reuseNode true
        }
      }
      environment {
        K8S_DIR = 'k8s'
        KUBECONFIG_PATH = "${env.HOME}/.kube/config"
      }
      steps {
        // kind-kubeconfig is the secret file credential you uploaded
        withCredentials([file(credentialsId: 'kind-kubeconfig', variable: 'KUBECONFIG_FILE')]) {
          sh '''
            set -e
            echo "Preparing kubeconfig..."
            mkdir -p $(dirname ${KUBECONFIG_PATH})
            cp "$KUBECONFIG_FILE" ${KUBECONFIG_PATH}
            chmod 600 ${KUBECONFIG_PATH}
            export KUBECONFIG=${KUBECONFIG_PATH}

            echo "kubectl client:"
            kubectl version --client --short || true
            echo "Cluster contexts:"
            kubectl config get-contexts || true

            echo "Applying manifests from ${K8S_DIR}..."
            kubectl apply -f ${K8S_DIR}

            echo "Waiting for deployments to rollout..."
            # iterate deployments in current namespace(s)
            DEPS=$(kubectl get deploy --all-namespaces -o jsonpath='{range .items[*]}{.metadata.namespace}{"|"}{.metadata.name}{"\n"}{end}' || true)
            if [ -z "$DEPS" ]; then
              echo "No deployments found to wait for."
            else
              echo "$DEPS" | while IFS='|' read -r NS D; do
                if [ -n "$D" ]; then
                  echo "Rollout status for deployment $D in namespace $NS ..."
                  kubectl -n "$NS" rollout status "deployment/$D" --timeout=180s || {
                    echo "Rollout failed for $D in $NS. Collecting debug info..."
                    kubectl -n "$NS" describe deployment "$D" || true
                    # show failing pods for this deployment
                    PODS=$(kubectl -n "$NS" get pods -l app="$D" -o name || true)
                    if [ -n "$PODS" ]; then
                      for p in $PODS; do
                        echo "=== Logs for $p ==="
                        kubectl -n "$NS" logs "$p" --all-containers || true
                      done
                    else
                      echo "No pods with label app=$D found; listing pods in namespace $NS:"
                      kubectl -n "$NS" get pods -o wide || true
                    fi
                    exit 1
                  }
                fi
              done
            fi

            echo "Final pods:"
            kubectl get pods --all-namespaces -o wide || true

            echo "Services:"
            kubectl get svc --all-namespaces -o wide || true
          '''
        }
      }
    }
    // ----------------- end Deploy stage -----------------

  } // end stages

  post {
    success { echo 'Pipeline finished successfully.' }
    failure {
      echo 'Pipeline failed — check console output.'
      // collect cluster events for debugging if kubeconfig present
      script {
        try {
          docker.image('bitnami/kubectl:1.29.6').inside {
            withCredentials([file(credentialsId: 'kind-kubeconfig', variable: 'KUBECONFIG_FILE')]) {
              sh '''
                mkdir -p $HOME/.kube
                cp "$KUBECONFIG_FILE" $HOME/.kube/config || true
                export KUBECONFIG=$HOME/.kube/config
                echo "Cluster events (last 50):"
                kubectl get events --all-namespaces --sort-by='.lastTimestamp' | tail -n 50 || true
              '''
            }
          }
        } catch (e) {
          echo "Post-failure debug step failed: ${e}"
        }
      }
    }
  }
}

