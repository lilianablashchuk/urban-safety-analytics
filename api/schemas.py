from pydantic import BaseModel, Field
from typing import List, Dict, Any

class IncidentFeatures(BaseModel):
    latitude: float = Field(..., ge=49.70, le=50.00, description="Spatial latitude coordinate")
    longitude: float = Field(..., ge=23.80, le=24.20, description="Spatial longitude coordinate")
    district: str = Field(..., description="Administrative municipal district")
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0-Mon, 6-Sun)")
    lux_level: float = Field(..., ge=0.0, le=1000.0, description="Ambient illuminance level in Lux")
    cctv_density: int = Field(..., ge=0, le=50, description="Number of CCTV cameras within 150m radius")
    venue_density: int = Field(..., ge=0, le=100, description="Number of nightlife/entertainment venues nearby")
    transit_dist_m: float = Field(..., ge=0.0, le=5000.0, description="Distance to nearest public transit stop (m)")
    is_weekend: int = Field(..., ge=0, le=1, description="Weekend binary indicator (0 or 1)")

class PredictionRequest(BaseModel):
    features: IncidentFeatures
    model_type: str = Field(default="stacking", description="ridge | random_forest | lightgbm | stacking")

class PredictionResponse(BaseModel):
    risk_score: float
    safety_tier: str
    confidence_interval: List[float]
    model_used: str

class BatchPredictionRequest(BaseModel):
    items: List[IncidentFeatures]
    model_type: str = Field(default="stacking")

class BatchPredictionResponse(BaseModel):
    count: int
    predictions: List[Dict[str, float]]
    mean_risk_score: float

class HotspotRequest(BaseModel):
    hour: int = Field(..., ge=0, le=23)
    eps_meters: float = Field(default=350.0, ge=50.0, le=2000.0)
    min_samples: int = Field(default=5, ge=2, le=50)

class HotspotResponse(BaseModel):
    hotspots_found: int
    clusters: List[Dict[str, object]]

class SafeRouteRequest(BaseModel):
    start_node: str
    end_node: str
    alpha: float = Field(default=0.5, ge=0.0, le=1.0)
    model_type: str = Field(default="stacking")

class SafeRouteResponse(BaseModel):
    path: List[str]
    total_distance_m: float
    average_risk: float
    integrated_cost: float
    nodes_coords: List[Dict[str, Any]]

class BenchmarkResponse(BaseModel):
    metrics: Dict[str, Dict[str, float]]
    feature_importance: Dict[str, float]
    trained_at: str
    total_samples: int