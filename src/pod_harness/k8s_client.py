from kubernetes import client

from pod_harness.config import Settings


def create_core_v1_api(settings: Settings) -> client.CoreV1Api:
    configuration = client.Configuration()
    configuration.host = settings.api_server
    configuration.verify_ssl = settings.verify_ssl
    if settings.verify_ssl and settings.ca_cert_file:
        configuration.ssl_ca_cert = settings.ca_cert_file

    configuration.api_key = {"authorization": settings.service_account_token}
    configuration.api_key_prefix = {"authorization": "Bearer"}

    api_client = client.ApiClient(configuration=configuration)
    return client.CoreV1Api(api_client=api_client)
