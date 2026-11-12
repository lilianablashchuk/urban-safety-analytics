from api.model_service import SafetyModelService

def test_model_bundle_integrity():
    service = SafetyModelService()
    assert service.bundle is not None
    for model_key in ["ridge", "random_forest", "lightgbm", "stacking"]:
        assert model_key in service.bundle["models"]
    assert "feature_importance" in service.bundle

def test_counterfactual_monotonicity():
    service = SafetyModelService()
    baseline = {
        "latitude": 49.8400,
        "longitude": 24.0300,
        "district": "Halytskyi",
        "hour": 23,
        "day_of_week": 5,
        "is_weekend": 1,
        "lux_level": 5.0,
        "cctv_density": 0,
        "venue_density": 20,
        "transit_dist_m": 200.0
    }
    upgraded = baseline.copy()
    upgraded["lux_level"] = 180.0
    upgraded["cctv_density"] = 12

    score_base = service.predict(baseline, model_type="stacking")["risk_score"]
    score_upgraded = service.predict(upgraded, model_type="stacking")["risk_score"]

    assert score_upgraded < score_base