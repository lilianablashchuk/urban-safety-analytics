from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

DATASET_PATH = DATA_DIR / "urban_safety_incidents.csv"
MODEL_BUNDLE_PATH = MODELS_DIR / "safety_system_bundle.joblib"
ROAD_GRAPH_PATH = DATA_DIR / "synthetic_city_graph.json"

CITY_BOUNDS = {
    "lat_min": 49.7800,
    "lat_max": 49.8800,
    "lon_min": 23.9500,
    "lon_max": 24.1000
}

DISTRICTS = [
    "Halytskyi",
    "Frankivskyi",
    "Shevchenkivskyi",
    "Lychakivskyi",
    "Sykhivskyi",
    "Zaliznychnyi"
]