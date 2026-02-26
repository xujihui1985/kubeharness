## Pod Harness

`pod-harness` is a Python e2e test harness for Kubernetes infra, managed by `uv`.

Each test file is a suite. The first suite validates pod lifecycle:

1. Create a pod via Kubernetes API
2. Wait until pod is `Running` and `Ready`
3. Delete the pod
4. Verify pod is deleted

Authentication is done with a service account token, not kubeconfig.

## Project Layout

```text
src/pod_harness/config.py         # env-driven runtime settings
src/pod_harness/k8s_client.py     # CoreV1Api client construction from SA token
src/pod_harness/pod_lifecycle.py  # pod create/wait/delete helpers
tests/e2e/test_pod_lifecycle.py   # first e2e suite
```

## Prerequisites

- Python 3.14
- `uv`
- Access to a Kubernetes API server
- A service account token with pod create/read/delete permissions in target namespace

## Configuration

Required:

- `K8S_API_SERVER`  
  Example: `https://10.0.0.1:6443`

Service account token (choose one):

- `K8S_SA_TOKEN` (raw token string), or
- `K8S_SA_TOKEN_FILE` (defaults to `/var/run/secrets/kubernetes.io/serviceaccount/token`)

Optional:

- `K8S_NAMESPACE` (default: `default`)
- `K8S_VERIFY_SSL` (default: `true`)
- `K8S_CA_CERT_FILE` (default: `/var/run/secrets/kubernetes.io/serviceaccount/ca.crt`)
- `POD_HARNESS_WAIT_TIMEOUT_SECONDS` (default: `120`)
- `POD_HARNESS_POLL_INTERVAL_SECONDS` (default: `2`)

## Run

Install dependencies:

```bash
uv venv --python 3.14
uv sync --dev
```

Run all e2e tests:

```bash
uv run pytest -m e2e
```
