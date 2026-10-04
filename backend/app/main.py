from fastapi import FastAPI, HTTPException
from kubernetes.client.exceptions import ApiException
from app.k8s_service import KubernetesService
k8s = KubernetesService()

app = FastAPI(
    title="K8s AI Support Platform",
    description="Backend API for Kubernetes AI support platform",
    version="1.1.0"
)


@app.get("/")
def root():
    return {
        "message": "K8s AI Support Platform API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/ready")
def ready():
    return {
        "status": "ready"
    }


@app.get("/k8s/pods")
def get_pods():
    v1 = get_k8s_client()

    pods = v1.list_namespaced_pod(
        namespace="k8s-ai-platform"
    )

    return {
        "pods": [
            {
                "name": pod.metadata.name,
                "status": pod.status.phase
            }
            for pod in pods.items
        ]
    }

@app.get("/api/k8s/pods")
def list_pods():
    try:
        return {"pods": k8s.list_pods()}
    except ApiException as e:
        raise HTTPException(
            status_code=e.status or 500,
            detail=e.reason
        )


@app.get("/api/k8s/pods/{pod_name}")
def get_pod(pod_name: str):
    try:
        return k8s.get_pod(pod_name)
    except ApiException as e:
        raise HTTPException(
            status_code=e.status or 500,
            detail=e.reason
        )


@app.get("/api/k8s/pods/{pod_name}/logs")
def pod_logs(pod_name: str):
    try:
        return {
            "pod": pod_name,
            "logs": k8s.get_pod_logs(pod_name)
        }
    except ApiException as e:
        raise HTTPException(
            status_code=e.status or 500,
            detail=e.reason
        )


@app.get("/api/k8s/deployments")
def list_deployments():
    try:
        return {
            "deployments": k8s.list_deployments()
        }
    except ApiException as e:
        raise HTTPException(
            status_code=e.status or 500,
            detail=e.reason
        )


@app.get("/api/k8s/events")
def list_events():
    try:
        return {
            "events": k8s.list_events()
        }
    except ApiException as e:
        raise HTTPException(
            status_code=e.status or 500,
            detail=e.reason
        )
@app.get("/api/k8s/pods/{pod_name}/diagnose")
def diagnose_pod(pod_name: str):
    try:
        return k8s.diagnose_pod(pod_name)

    except ApiException as e:
        raise HTTPException(
            status_code=e.status or 500,
            detail=e.reason
        )    