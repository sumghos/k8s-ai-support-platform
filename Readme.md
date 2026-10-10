# Kubernetes AI Support Platform

A hands-on project for building a Kubernetes troubleshooting platform
with a Python FastAPI backend, Minikube, and a future chatbot/LLM layer.
The project is being developed incrementally, with an emphasis on
learning Kubernetes concepts and building reusable tools before
introducing an LLM.

> **Project status:** Core backend and Kubernetes diagnostic
> capabilities are being developed. Check the implementation checklist
> below and the actual repository code before treating every planned
> capability as complete.

## Goals

-   Run a Python API on Kubernetes.
-   Inspect pods, deployments, logs, and namespace events through the
    Kubernetes Python SDK.
-   Build reusable Kubernetes tools and a diagnostic orchestrator.
-   Detect common pod/container failure patterns and recommend
    investigation steps.
-   Add a chatbot and LLM integration in a later phase.
-   Extend toward production-style observability, security, and cloud
    deployment.

## Current technology stack

-   **Language:** Python 3.12
-   **API:** FastAPI, Uvicorn
-   **Containerization:** Docker
-   **Kubernetes development cluster:** Minikube
-   **Kubernetes client:** Kubernetes Python SDK
-   **API testing:** FastAPI Swagger UI
-   **Source control:** Git and GitHub

## Architecture

``` text
Future Chatbot UI
       |
       v
FastAPI endpoints
       |
       v
Diagnostic Orchestrator
       |
       v
Kubernetes Tools
       |
       v
Kubernetes Service
       |
       v
Minikube / Kubernetes API
```

The current diagnostic workflow is intended to gather pod details,
container health information, logs, and namespace events. A rules engine
can then convert those observations into structured findings and
recommended next steps. The LLM/chatbot layer is a future milestone, not
a prerequisite for the current API.

## Repository structure

The following is the expected project layout based on the work to date.
Your local repository may differ; keep the tree aligned with files that
actually exist.

``` text
k8s-ai-support-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── k8s_service.py
│   │   ├── k8s_tools.py
│   │   ├── diagnostics.py
│   │   └── diagnostic_rules.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/
│   ├── src/
│   │   └── index.html
│   ├── nginx.conf
│   ├── Dockerfile
│   └── .dockerignore
├── k8s/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   └── frontend-service.yaml
└── README.md
```

Some files in this tree were introduced during the day-by-day plan.
Confirm each file exists before relying on it.

## Backend API

The endpoints below are the planned/current development interface. They
should be verified in Swagger (`/docs`) against the running version of
the code.

  -------------------------------------------------------------------------------------------
  Method                  Endpoint                                    Purpose
  ----------------------- ------------------------------------------- -----------------------
  GET                     `/`                                         API welcome message

  GET                     `/health`                                   Liveness-style health
                                                                      response

  GET                     `/ready`                                    Readiness-style
                                                                      response

  GET                     `/api/k8s/pods`                             List pods in the
                                                                      configured namespace

  GET                     `/api/k8s/pods/{pod_name}`                  Get a pod's details

  GET                     `/api/k8s/pods/{pod_name}/logs`             Retrieve recent pod
                                                                      logs

  GET                     `/api/k8s/pods/{pod_name}/diagnose`         Inspect pod/container
                                                                      health

  GET                     `/api/k8s/deployments`                      List deployments and
                                                                      replica status

  GET                     `/api/k8s/events`                           List events in the
                                                                      configured namespace

  GET                     `/api/k8s/pods/{pod_name}/full-diagnosis`   Combine pod details,
                                                                      diagnosis, logs,
                                                                      events, and (when
                                                                      integrated) rule-based
                                                                      findings
  -------------------------------------------------------------------------------------------

The namespace used in the current examples is `k8s-ai-platform`. Verify
that `NAMESPACE` in the backend matches your Kubernetes namespace.

## Prerequisites

Install and configure:

-   Python 3.12 or a compatible Python version
-   Docker
-   Minikube
-   `kubectl`
-   Git

Check Minikube and the active Kubernetes context:

``` powershell
minikube status
kubectl config current-context
kubectl get nodes
kubectl get pods -n k8s-ai-platform
```

The active context should be `minikube` when you intend to use your
local Minikube cluster.

## Run the backend locally

From the repository root:

``` powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the interactive API documentation:

-   Swagger UI: <http://127.0.0.1:8000/docs>
-   Root endpoint: <http://127.0.0.1:8000/>
-   Health endpoint: <http://127.0.0.1:8000/health>

The Kubernetes Python client must load the kubeconfig when running
locally, for example with `config.load_kube_config()`, before creating
API clients. This lets the client use the configured Minikube context
instead of defaulting to `localhost:80`.

## Build and load container images

Build the backend image:

``` powershell
cd backend
docker build -t k8s-ai-backend:dev .
```

If the frontend files are present, build its image:

``` powershell
cd ..\frontend
docker build -t k8s-ai-frontend:dev .
```

Load locally built images into Minikube so the cluster can use them:

``` powershell
minikube image load k8s-ai-backend:dev
minikube image load k8s-ai-frontend:dev
minikube image ls
```

These commands assume the images were built successfully and the
Kubernetes manifests reference the same image tags. With
`imagePullPolicy: Never`, the image must already be available inside
Minikube's image runtime.

## Deploy Kubernetes resources

From the repository root, apply the manifests that exist in your `k8s/`
directory:

``` powershell
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
```

Check rollout and resources:

``` powershell
kubectl rollout status deployment/backend -n k8s-ai-platform
kubectl get deployments,services,pods -n k8s-ai-platform
kubectl get events -n k8s-ai-platform --sort-by=.metadata.creationTimestamp
```

If a manifest is not yet created, skip its command until it exists. For
cluster access, port-forwarding is a simple local development option:

``` powershell
kubectl port-forward service/backend-service 8000:80 -n k8s-ai-platform
```

Use a different local port if it conflicts with the locally running
Uvicorn process. Ingress access depends on your Minikube driver and
ingress configuration.

## Development roadmap

This is the learning sequence, not a claim that every item is complete.

-   [x] Project repository and initial FastAPI backend
-   [x] Containerization with Docker (image build should be verified
    locally)
-   [x] Initial Kubernetes manifests for namespace, configuration,
    deployment, and service
-   [x] Health/readiness endpoints and deployment probe concepts
-   [x] Frontend starter and frontend Kubernetes manifests
-   [x] Kubernetes Python SDK connection work
-   [x] Reusable Kubernetes service/tool-layer design
-   [ ] Verify pod listing, pod details, logs, deployments, and events
    end-to-end
-   [ ] Verify combined diagnostic endpoint
-   [ ] Integrate and test rule-based findings and recommendations
-   [ ] Add tests and stronger input/error validation
-   [ ] Add previous-container log retrieval and deeper failure
    diagnostics
-   [ ] Build the chatbot UI and connect it to the backend
-   [ ] Add an LLM agent with controlled tool access
-   [ ] Add authentication, authorization, and audit logging
-   [ ] Add observability, CI/CD, and cloud/AKS deployment

Only mark a task complete after validating it in the current code and
environment.

## Security notes

-   Do not commit real secrets, access tokens, kubeconfig files, or
    credentials.
-   The example Kubernetes Secret value `change-me` is a placeholder,
    not a production secret.
-   Keep diagnostic APIs local while developing. Pod logs and Kubernetes
    events may expose sensitive infrastructure or application data.
-   Before sharing the API, implement authentication and authorization,
    input validation, sanitized error responses, and audit logging.
-   Begin with read-only Kubernetes permissions. Any future remediation
    or write operation should require explicit authorization and
    appropriate safeguards.

## Troubleshooting

### Kubernetes client tries `localhost:80`

When running FastAPI directly on Windows, load the local kubeconfig
before creating Kubernetes clients:

``` python
from kubernetes import config
config.load_kube_config()
```

Then verify the context:

``` powershell
kubectl config current-context
```

### Pod is not starting

``` powershell
kubectl get pods -n k8s-ai-platform
kubectl describe pod <pod-name> -n k8s-ai-platform
kubectl logs <pod-name> -n k8s-ai-platform --all-containers=true
kubectl get events -n k8s-ai-platform --sort-by=.metadata.creationTimestamp
```

For a restarted container, inspect the previous instance's logs:

``` powershell
kubectl logs <pod-name> -n k8s-ai-platform --previous
```

### Image is not found by Minikube
``` powershell
minikube image load k8s-ai-backend:dev
minikube image ls
```

Check that the image name/tag in the Deployment matches the loaded image
and that the pull policy matches the local-image workflow.

## Contributing / next steps

This is a learning project. Make incremental changes, validate each
endpoint and Kubernetes resource, and record the results before adding
the next layer. The immediate priority is to make the existing
Kubernetes diagnostic path reliable; LLM integration comes after the
underlying tools are tested.
