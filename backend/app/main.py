from fastapi import FastAPI

app = FastAPI(
    title="K8s AI Support Platform",
    description="Backend API for Kubernetes AI support platform",
    version="1.0.0"
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