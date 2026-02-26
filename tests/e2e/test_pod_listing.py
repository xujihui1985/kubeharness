from uuid import uuid4

import pytest

from kubeharness.config import Settings
from kubeharness.pod_lifecycle import (
    create_sleep_pod,
    delete_pod,
    wait_for_pod_deleted,
    wait_for_pod_running_and_ready,
    list_pods,
)


@pytest.mark.e2e
def test_list_pods(core_v1_api, settings: Settings) -> None:
    pod_name = f"pod-harness-{uuid4().hex[:10]}"

    create_sleep_pod(
        api=core_v1_api,
        namespace=settings.namespace,
        name=pod_name,
    )

    try:
        wait_for_pod_running_and_ready(
            api=core_v1_api,
            namespace=settings.namespace,
            name=pod_name,
            timeout_seconds=settings.wait_timeout_seconds,
            poll_interval_seconds=settings.poll_interval_seconds,
        )

        pods = list_pods(api=core_v1_api, namespace=settings.namespace)
        pod_names = [pod.metadata.name for pod in pods.items]
        assert pod_name in pod_names

    finally:
        delete_pod(api=core_v1_api, namespace=settings.namespace, name=pod_name)
        wait_for_pod_deleted(
            api=core_v1_api,
            namespace=settings.namespace,
            name=pod_name,
            timeout_seconds=settings.wait_timeout_seconds,
            poll_interval_seconds=settings.poll_interval_seconds,
        )
