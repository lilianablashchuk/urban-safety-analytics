import requests
import streamlit as st
from typing import Dict, Any, List

@st.cache_resource
def get_http_session() -> requests.Session:
    return requests.Session()

@st.cache_data(ttl=300, show_spinner=False)
def _cached_post(url: str, payload_json: str, timeout: int = 15) -> Dict[str, Any]:
    session = get_http_session()
    resp = session.post(url, data=payload_json, headers={"Content-Type": "application/json"}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

@st.cache_data(ttl=60, show_spinner=False)
def _cached_get(url: str, timeout: int = 10) -> Dict[str, Any]:
    session = get_http_session()
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

class SafetyAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def get_health(self) -> Dict[str, Any]:
        return _cached_get(f"{self.base_url}/health", timeout=3)

    def get_benchmark(self) -> Dict[str, Any]:
        return _cached_get(f"{self.base_url}/models/benchmark", timeout=10)

    def retrain(self) -> Dict[str, Any]:
        session = get_http_session()
        resp = session.post(f"{self.base_url}/train", timeout=60)
        resp.raise_for_status()
        st.cache_data.clear()  
        return resp.json()

    def predict_safety(self, features: Dict[str, Any], model_type: str = "stacking") -> Dict[str, Any]:
        import json
        payload = json.dumps({"features": features, "model_type": model_type}, sort_keys=True)
        return _cached_post(f"{self.base_url}/predict/safety", payload, timeout=5)

    def predict_batch(self, items: List[Dict[str, Any]], model_type: str = "stacking") -> Dict[str, Any]:
        import json
        payload = json.dumps({"items": items, "model_type": model_type})
        return _cached_post(f"{self.base_url}/predict/batch", payload, timeout=25)

    def get_hotspots(self, hour: int, eps_meters: float = 350.0, min_samples: int = 5) -> Dict[str, Any]:
        import json
        payload = json.dumps({"hour": hour, "eps_meters": eps_meters, "min_samples": min_samples}, sort_keys=True)
        return _cached_post(f"{self.base_url}/analytics/hotspots", payload, timeout=10)

    def get_safe_route(self, start_node: str, end_node: str, alpha: float, model_type: str = "stacking") -> Dict[str, Any]:
        import json
        payload = json.dumps({"start_node": start_node, "end_node": end_node, "alpha": alpha, "model_type": model_type}, sort_keys=True)
        return _cached_post(f"{self.base_url}/routing/safe-path", payload, timeout=10)