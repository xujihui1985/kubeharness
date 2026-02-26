from collections.abc import Iterator

import pytest
from kubernetes import client

from kubeharness.config import Settings
from kubeharness.k8s_client import create_core_v1_api


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture()
def core_v1_api(settings: Settings) -> Iterator[client.CoreV1Api]:
    api = create_core_v1_api(settings)
    try:
        yield api
    finally:
        api.api_client.close()
