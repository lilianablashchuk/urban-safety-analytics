from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["models_loaded"] is True

def test_pydantic_validation_error():
    invalid_payload = {
        "features": {
            "latitude": 49.8400,
            "longitude": 24.0300,
            "district": "Halytskyi",
            "hour": 29,  # Invalid hour > 23
            "day_of_week": 2,
            "lux_level": 50.0,
            "cctv_density": 5,
            "venue_density": 2,
            "transit_dist_m": 100.0,
            "is_weekend": 0
        },
        "model_type": "stacking"
    }
    response = client.post("/predict/safety", json=invalid_payload)
    assert response.status_code == 422

def test_predict_safety_endpoint():
    valid_payload = {
        "features": {
            "latitude": 49.8400,
            "longitude": 24.0300,
            "district": "Halytskyi",
            "hour": 22,
            "day_of_week": 4,
            "lux_level": 12.0,
            "cctv_density": 3,
            "venue_density": 14,
            "transit_dist_m": 120.0,
            "is_weekend": 0
        },
        "model_type": "stacking"
    }
    response = client.post("/predict/safety", json=valid_payload)
    assert response.status_code == 200
    data = response.json()
    assert 0.0 <= data["risk_score"] <= 100.0
    assert data["safety_tier"] in ["Safe", "Caution", "High Alert"]

def test_safe_routing_endpoint():
    payload = {
        "start_node": "Node_0_0",
        "end_node": "Node_4_4",
        "alpha": 0.2
    }
    response = client.post("/routing/safe-path", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["path"]) >= 2
    assert data["total_distance_m"] > 0