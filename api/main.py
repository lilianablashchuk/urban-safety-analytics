from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from api.schemas import (
    PredictionRequest, PredictionResponse,
    BatchPredictionRequest, BatchPredictionResponse,
    HotspotRequest, HotspotResponse,
    SafeRouteRequest, SafeRouteResponse,
    BenchmarkResponse
)
from api.model_service import model_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not model_service.bundle:
        model_service.load_or_train()
    yield

app = FastAPI(
    title="Urban Safety Analytics & Safe Routing Engine",
    version="1.0.0",
    description="REST API for heterogeneous ML ensemble inference, DBSCAN hotspot clustering, and safety-weighted routing.",
    lifespan=lifespan
)

@app.get("/health")
def health():
    return {
        "status": "online",
        "models_loaded": model_service.bundle is not None,
        "available_models": list(model_service.bundle["models"].keys()) if model_service.bundle else []
    }

@app.post("/train", response_model=BenchmarkResponse)
def train():
    bundle = model_service.train_all_models()
    return {
        "metrics": bundle["metrics"],
        "feature_importance": bundle["feature_importance"],
        "trained_at": bundle["trained_at"],
        "total_samples": bundle["total_samples"]
    }

@app.post("/predict/safety", response_model=PredictionResponse)
def predict_safety(req: PredictionRequest):
    try:
        return model_service.predict(req.features.model_dump(), model_type=req.model_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(req: BatchPredictionRequest):
    try:
        raw_items = [item.model_dump() for item in req.items]
        return model_service.predict_batch(raw_items, model_type=req.model_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analytics/hotspots", response_model=HotspotResponse)
def analytics_hotspots(req: HotspotRequest):
    try:
        return model_service.find_hotspots(req.hour, req.eps_meters, req.min_samples)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/routing/safe-path", response_model=SafeRouteResponse)
def routing_safe_path(req: SafeRouteRequest):
    try:
        return model_service.calculate_safe_route(req.start_node, req.end_node, req.alpha, req.model_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/models/benchmark", response_model=BenchmarkResponse)
def get_benchmark():
    if not model_service.bundle:
        raise HTTPException(status_code=400, detail="Models are not initialized.")
    return {
        "metrics": model_service.bundle["metrics"],
        "feature_importance": model_service.bundle["feature_importance"],
        "trained_at": model_service.bundle["trained_at"],
        "total_samples": model_service.bundle["total_samples"]
    }