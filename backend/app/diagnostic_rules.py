
class DiagnosticRules:
    """Convert Kubernetes observations into actionable findings."""

    def analyze(self, pod_name, pod_details, diagnosis, events):
        findings = []
        phase = (pod_details or {}).get("status", "Unknown")

        def add_finding(code, severity, message, evidence, recommendation):
            findings.append({
                "code": code,
                "severity": severity,
                "message": message,
                "evidence": evidence,
                "recommendation": recommendation,
            })

        # Rule 1: Pod is not running
        if phase == "Pending":
            add_finding(
                "POD_PENDING",
                "warning",
                "The pod has not reached the Running phase.",
                f"Pod phase: {phase}",
                "Inspect pod events and scheduling details "
                "to identify why the pod is pending.",
            )

        elif phase == "Failed":
            add_finding(
                "POD_FAILED",
                "critical",
                "The pod has entered the Failed phase.",
                f"Pod phase: {phase}",
                "Inspect container termination details and "
                "pod events to determine the failure cause.",
            )

        # Rule 2: Inspect container states and restart counts
        for container in (diagnosis or {}).get("containers", []):
            name = container.get("name", "unknown")
            state = container.get("state")
            reason = container.get("reason")
            restarts = container.get("restart_count", 0)

            if reason == "CrashLoopBackOff":
                add_finding(
                    "CRASH_LOOP_BACK_OFF",
                    "critical",
                    f"Container {name} repeatedly fails to start.",
                    f"Container state reason: {reason}",
                    "Inspect previous container logs, exit codes, "
                    "application configuration, and resource limits.",
                )

            elif reason in ("ImagePullBackOff", "ErrImagePull"):
                add_finding(
                    "IMAGE_PULL_FAILURE",
                    "critical",
                    f"Container {name} cannot pull its image.",
                    f"Container state reason: {reason}",
                    "Verify the image name and tag, image availability, "
                    "registry access, and image pull credentials.",
                )

            elif state == "Waiting" and reason not in (
                None, "ContainerCreating"
            ):
                add_finding(
                    "CONTAINER_WAITING",
                    "warning",
                    f"Container {name} is waiting to start.",
                    f"Waiting reason: {reason}",
                    "Inspect pod events for the specific reason "
                    "the container cannot start.",
                )

            if restarts >= 3:
                add_finding(
                    "REPEATED_RESTARTS",
                    "warning",
                    f"Container {name} has restarted repeatedly.",
                    f"Restart count: {restarts}",
                    "Inspect current and previous container logs, "
                    "exit codes, and probe failures.",
                )

            if container.get("ready") is False:
                add_finding(
                    "CONTAINER_NOT_READY",
                    "warning",
                    f"Container {name} is not ready.",
                    "Container readiness is false.",
                    "Check readiness probe configuration and "
                    "application health.",
                )

        # Rule 3: Match warning events to this pod
        pod_events = [
            event for event in (events or [])
            if event.get("object") == pod_name
        ]

        for event in pod_events:
            if event.get("type") == "Warning":
                add_finding(
                    "KUBERNETES_WARNING_EVENT",
                    "warning",
                    event.get("reason") or "Kubernetes warning event",
                    event.get("message") or "No event message available.",
                    "Investigate the event message and related "
                    "container or scheduling configuration.",
                )

        if not findings:
            add_finding(
                "NO_KNOWN_ISSUES",
                "info",
                "No known issues were detected by the current rules.",
                f"Pod phase: {phase}",
                "Continue monitoring the pod. This result does not "
                "guarantee that the application is error-free.",
            )

        return {
            "pod": pod_name,
            "overall_status": self._overall_status(findings),
            "finding_count": len(findings),
            "findings": findings,
        }

    @staticmethod
    def _overall_status(findings):
        severities = {item["severity"] for item in findings}

        if "critical" in severities:
            return "critical"
        if "warning" in severities:
            return "warning"
        return "healthy"
