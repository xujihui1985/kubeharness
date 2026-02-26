from uuid import uuid4

import pytest

from pod_harness.config import Settings
from pod_harness.pod_lifecycle import (
    create_sleep_pod,
    delete_pod,
    wait_for_pod_deleted,
    wait_for_pod_running_and_ready,
)


@pytest.mark.e2e
def test_create_verify_and_delete_pod(core_v1_api, settings: Settings) -> None:
    pod_name = f"pod-harness-{uuid4().hex[:10]}"

    create_sleep_pod(
        api=core_v1_api,
        namespace=settings.namespace,
        name=pod_name,
    )

    try:
        pod = wait_for_pod_running_and_ready(
            api=core_v1_api,
            namespace=settings.namespace,
            name=pod_name,
            timeout_seconds=settings.wait_timeout_seconds,
            poll_interval_seconds=settings.poll_interval_seconds,
        )
        assert pod.status is not None
        assert pod.status.phase == "Running"
    finally:
        delete_pod(api=core_v1_api, namespace=settings.namespace, name=pod_name)
        wait_for_pod_deleted(
            api=core_v1_api,
            namespace=settings.namespace,
            name=pod_name,
            timeout_seconds=settings.wait_timeout_seconds,
            poll_interval_seconds=settings.poll_interval_seconds,
        )
