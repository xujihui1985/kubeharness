from typing import Self
from dataclasses import dataclass
from pathlib import Path
import os


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _read_token(token: str | None, token_file: str | None) -> str:
    if token and token.strip():
        return token.strip()

    if not token_file:
        raise ValueError(
            "K8S_SA_TOKEN or K8S_SA_TOKEN_FILE must be set for service-account authentication."
        )

    token_path = Path(token_file)
    if not token_path.exists():
        raise ValueError(f"Service-account token file not found: {token_file}")

    loaded = token_path.read_text(encoding="utf-8").strip()
    if not loaded:
        raise ValueError(f"Service-account token file is empty: {token_file}")
    return loaded


@dataclass(frozen=True)
class Settings:
    api_server: str
    namespace: str
    service_account_token: str
    verify_ssl: bool
    ca_cert_file: str | None
    wait_timeout_seconds: int
    poll_interval_seconds: float

    @classmethod
    def from_env(cls) -> Self:
        api_server = os.getenv("K8S_API_SERVER", "").strip()
        if not api_server:
            raise ValueError("K8S_API_SERVER is required, e.g. https://10.0.0.1:6443")

        namespace = os.getenv("K8S_NAMESPACE", "default").strip() or "default"
        verify_ssl = _env_bool("K8S_VERIFY_SSL", True)
        ca_cert_file = os.getenv(
            "K8S_CA_CERT_FILE", "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
        ).strip()
        token = _read_token(
            token=os.getenv("K8S_SA_TOKEN"),
            token_file=os.getenv(
                "K8S_SA_TOKEN_FILE",
                "/var/run/secrets/kubernetes.io/serviceaccount/token",
            ).strip(),
        )
        wait_timeout_seconds = int(os.getenv("POD_HARNESS_WAIT_TIMEOUT_SECONDS", "120"))
        poll_interval_seconds = float(os.getenv("POD_HARNESS_POLL_INTERVAL_SECONDS", "2"))

        if wait_timeout_seconds <= 0:
            raise ValueError("POD_HARNESS_WAIT_TIMEOUT_SECONDS must be > 0")
        if poll_interval_seconds <= 0:
            raise ValueError("POD_HARNESS_POLL_INTERVAL_SECONDS must be > 0")

        if verify_ssl and not ca_cert_file:
            raise ValueError("K8S_CA_CERT_FILE must be set when K8S_VERIFY_SSL=true")

        return cls(
            api_server=api_server,
            namespace=namespace,
            service_account_token=token,
            verify_ssl=verify_ssl,
            ca_cert_file=ca_cert_file if ca_cert_file else None,
            wait_timeout_seconds=wait_timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )
