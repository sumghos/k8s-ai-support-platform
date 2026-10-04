from kubernetes import client, config
from kubernetes.client.exceptions import ApiException


NAMESPACE = "k8s-ai-platform"


class KubernetesService:

    def __init__(self):
        config.load_kube_config()

        self.core_api = client.CoreV1Api()
        self.apps_api = client.AppsV1Api()

    def list_pods(self):
        pods = self.core_api.list_namespaced_pod(
            namespace=NAMESPACE
        )

        return [
            {
                "name": pod.metadata.name,
                "status": pod.status.phase,
                "node": pod.spec.node_name,
            }
            for pod in pods.items
        ]

    def get_pod(self, pod_name):
        pod = self.core_api.read_namespaced_pod(
            name=pod_name,
            namespace=NAMESPACE
        )

        return {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "status": pod.status.phase,
            "node": pod.spec.node_name,
            "pod_ip": pod.status.pod_ip,
            "host_ip": pod.status.host_ip,
        }

    def get_pod_logs(self, pod_name):
        return self.core_api.read_namespaced_pod_log(
            name=pod_name,
            namespace=NAMESPACE,
            tail_lines=100
        )

    def list_deployments(self):
        deployments = self.apps_api.list_namespaced_deployment(
            namespace=NAMESPACE
        )

        return [
            {
                "name": deployment.metadata.name,
                "replicas": deployment.spec.replicas,
                "available": deployment.status.available_replicas or 0,
                "ready": deployment.status.ready_replicas or 0,
            }
            for deployment in deployments.items
        ]

    def list_events(self):
        events = self.core_api.list_namespaced_event(
            namespace=NAMESPACE
        )

        return [
            {
                "type": event.type,
                "reason": event.reason,
                "message": event.message,
                "object": (
                    event.involved_object.name
                    if event.involved_object
                    else None
                ),
                "last_timestamp": str(event.last_timestamp),
            }
            for event in events.items
        ]
    def diagnose_pod(self, pod_name):
        pod = self.core_api.read_namespaced_pod(
            name=pod_name,
            namespace=NAMESPACE
        )

        diagnosis = {
            "pod": pod.metadata.name,
            "phase": pod.status.phase,
            "node": pod.spec.node_name,
            "pod_ip": pod.status.pod_ip,
            "containers": [],
            "issues": []
        }

        if not pod.status.container_statuses:
            diagnosis["issues"].append(
                "No container status information available"
            )
            return diagnosis

        for container in pod.status.container_statuses:

            container_info = {
                "name": container.name,
                "ready": container.ready,
                "restart_count": container.restart_count
            }

            if container.state.waiting:
                container_info["state"] = "Waiting"
                container_info["reason"] = (
                    container.state.waiting.reason
                )
                container_info["message"] = (
                    container.state.waiting.message
                )

                diagnosis["issues"].append(
                    f"Container {container.name} is waiting: "
                    f"{container.state.waiting.reason}"
                )

            elif container.state.terminated:
                container_info["state"] = "Terminated"
                container_info["reason"] = (
                    container.state.terminated.reason
                )
                container_info["exit_code"] = (
                    container.state.terminated.exit_code
                )

                diagnosis["issues"].append(
                    f"Container {container.name} terminated: "
                    f"{container.state.terminated.reason}"
                )

            elif container.state.running:
                container_info["state"] = "Running"

            if container.restart_count > 0:
                diagnosis["issues"].append(
                    f"Container {container.name} restarted "
                    f"{container.restart_count} times"
                )

            if not container.ready:
                diagnosis["issues"].append(
                    f"Container {container.name} is not ready"
                )

            diagnosis["containers"].append(container_info)

        return diagnosis