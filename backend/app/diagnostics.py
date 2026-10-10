
from app.k8s_tools import KubernetesTools
from app.diagnostic_rules import DiagnosticRules



class DiagnosticOrchestrator:
    def __init__(self):
        self.tools = KubernetesTools()
        self.rules = DiagnosticRules()

    def diagnose_pod(self, pod_name: str):
        result = {
            "pod": pod_name,
            "pod_details": None,
            "diagnosis": None,
            "logs": None,
            "events": [],
            "errors": [],
        }

        # 1. Retrieve pod details
        try:
            result["pod_details"] = self.tools.get_pod(pod_name)
        except Exception as exc:
            result["errors"].append({
                "operation": "get_pod",
                "message": str(exc),
            })
            return result

        # 2. Analyze container health
        try:
            result["diagnosis"] = self.tools.diagnose_pod(pod_name)
        except Exception as exc:
            result["errors"].append({
                "operation": "diagnose_pod",
                "message": str(exc),
            })

        # 3. Retrieve recent logs
        try:
            result["logs"] = self.tools.get_pod_logs(pod_name)
        except Exception as exc:
            result["errors"].append({
                "operation": "get_pod_logs",
                "message": str(exc),
            })

        # 4. Retrieve namespace events
        try:
            result["events"] = self.tools.list_events()
        except Exception as exc:
            result["errors"].append({
                "operation": "list_events",
                "message": str(exc),
            })
        if result["pod_details"] is not None:
            result["analysis"] = self.rules.analyze(
                pod_name=pod_name,
                pod_details=result["pod_details"],
                diagnosis=result["diagnosis"],
                events=result["events"],
            )
        else:
            result["analysis"] = None    

        return result
