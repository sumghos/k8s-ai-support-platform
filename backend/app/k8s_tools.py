
from app.k8s_service import KubernetesService


class KubernetesTools:
    """Reusable tools for Kubernetes operations."""

    def __init__(self):
        self.k8s = KubernetesService()

    def list_pods(self):
        return self.k8s.list_pods()

    def get_pod(self, pod_name: str):
        return self.k8s.get_pod(pod_name)

    def get_pod_logs(self, pod_name: str):
        return self.k8s.get_pod_logs(pod_name)

    def list_deployments(self):
        return self.k8s.list_deployments()

    def list_events(self):
        return self.k8s.list_events()

    def diagnose_pod(self, pod_name: str):
        return self.k8s.diagnose_pod(pod_name)
