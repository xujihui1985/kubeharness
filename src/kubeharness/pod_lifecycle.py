from collections.abc import Iterable
from time import monotonic, sleep

from kubernetes import client
from kubernetes.client.exceptions import ApiException


def create_sleep_pod(
    api: client.CoreV1Api,
    namespace: str,
    name: str,
    image: str = "busybox:1.36",
    sleep_seconds: int = 120,
) -> client.V1Pod:
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name=name, labels={"app": "pod-harness"}),
        spec=client.V1PodSpec(
            restart_policy="Never",
            containers=[
                client.V1Container(
                    name="main",
                    image=image,
                    command=["sh", "-c", f"sleep {sleep_seconds}"],
                )
            ],
        ),
    )
    return api.create_namespaced_pod(namespace=namespace, body=pod)


def _conditions_to_map(conditions: Iterable[client.V1PodCondition] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    if not conditions:
        return result
    for condition in conditions:
        if condition.type and condition.status:
            result[condition.type] = condition.status
    return result


def wait_for_pod_running_and_ready(
    api: client.CoreV1Api,
    namespace: str,
    name: str,
    timeout_seconds: int,
    poll_interval_seconds: float,
) -> client.V1Pod:
    deadline = monotonic() + timeout_seconds
    last_seen: client.V1Pod | None = None

    while monotonic() < deadline:
        pod = api.read_namespaced_pod(name=name, namespace=namespace)
        last_seen = pod

        phase = pod.status.phase if pod.status else None
        conditions = _conditions_to_map(pod.status.conditions if pod.status else None)
        ready = conditions.get("Ready") == "True"

        if phase == "Running" and ready:
            return pod

        if phase in {"Failed", "Unknown"}:
            raise AssertionError(
                f"Pod {namespace}/{name} entered terminal unhealthy phase: {phase}; "
                f"conditions={conditions}"
            )

        sleep(poll_interval_seconds)

    if not last_seen:
        raise AssertionError(f"Pod {namespace}/{name} was never observed before timeout.")

    phase = last_seen.status.phase if last_seen.status else None
    conditions = _conditions_to_map(last_seen.status.conditions if last_seen.status else None)
    raise AssertionError(
        f"Timed out waiting for pod {namespace}/{name} to be Running+Ready. "
        f"last_phase={phase}, last_conditions={conditions}"
    )


def delete_pod(api: client.CoreV1Api, namespace: str, name: str) -> None:
    try:
        api.delete_namespaced_pod(
            name=name,
            namespace=namespace,
            body=client.V1DeleteOptions(grace_period_seconds=0),
        )
    except ApiException as exc:
        if exc.status != 404:
            raise


def wait_for_pod_deleted(
    api: client.CoreV1Api,
    namespace: str,
    name: str,
    timeout_seconds: int,
    poll_interval_seconds: float,
) -> None:
    deadline = monotonic() + timeout_seconds
    while monotonic() < deadline:
        try:
            api.read_namespaced_pod(name=name, namespace=namespace)
        except ApiException as exc:
            if exc.status == 404:
                return
            raise
        sleep(poll_interval_seconds)

    raise AssertionError(f"Timed out waiting for pod deletion: {namespace}/{name}")


def list_pods(api: client.CoreV1Api, namespace: str) -> client.V1PodList:
    return api.list_namespaced_pod(namespace=namespace)
