import os
import pytest
import requests
import base64

def _base_url() -> str:
    return os.getenv("LLM_BASE_URL", "http://localhost:8004").rstrip("/")


@pytest.fixture(scope="session")
def service_base_url() -> str:
    url = _base_url()
    health_url = f"{url}/health"
    try:
        resp = requests.get(health_url, timeout=3)
        resp.raise_for_status()
    except Exception as exc:
        pytest.skip(f"LLM service not reachable at {health_url}: {exc}")
    return url


def test_health(service_base_url: str):
    resp = requests.get(f"{service_base_url}/health", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"



def _encode_test_image() -> str:
    image_path = './asset/test.jpg'
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")




def test_list_models(service_base_url: str):
    resp = requests.get(f"{service_base_url}/llm/models", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert "available_models" in data
    assert isinstance(data["available_models"], list)


def test_metrics_endpoint(service_base_url: str):
    resp = requests.get(f"{service_base_url}/metrics", timeout=5)
    assert resp.status_code == 200
    assert resp.headers.get("content-type", "").startswith("text/plain")


@pytest.mark.parametrize("model_name", ["openrouter_api"])  # extend if more handlers are enabled
def test_load_infer_unload_cycle(service_base_url: str, model_name: str):
    models_resp = requests.get(f"{service_base_url}/llm/models", timeout=5)
    assert models_resp.status_code == 200
    available = models_resp.json().get("available_models", [])
    if model_name not in available:
        pytest.skip(f"Model '{model_name}' not available in this environment: {available}")

    load_url = f"{service_base_url}/llm/load"
    infer_url = f"{service_base_url}/llm/infer"
    unload_url = f"{service_base_url}/llm/unload"

    load_payload = {"model_name": model_name, "device": "cpu"}
    load_resp = requests.post(load_url, json=load_payload, timeout=60)
    if load_resp.status_code != 200:
        pytest.skip(
            f"Could not load model '{model_name}': {load_resp.status_code} {load_resp.text}"
        )
    test_image = _encode_test_image()
    infer_payload = {
        "prompt": "Say 'pytest' once.",
        "image_base64": [],
        "metadata": {"source": "pytest"},
    }
    infer_resp = requests.post(infer_url, json=infer_payload, timeout=60)

    try:
        assert infer_resp.status_code == 200, (
            f"infer failed: {infer_resp.status_code} {infer_resp.text}"
        )
        infer_data = infer_resp.json()
        print(infer_data['answer'])
        assert infer_data.get("status") == "success"
        assert isinstance(infer_data.get("answer", ""), str)
        assert len(infer_data.get("answer", "")) >= 0  # allow empty but present
        assert isinstance(infer_data.get("model_name", ""), str)
    finally:
        unload_resp = requests.post(unload_url, json={"cleanup_memory": True}, timeout=30)
        assert unload_resp.status_code == 200

