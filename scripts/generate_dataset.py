import json
import numpy as np
import pandas as pd
from api.config import DATASET_PATH, ROAD_GRAPH_PATH, CITY_BOUNDS, DISTRICTS

def generate_spatial_dataset(n_samples: int = 5000) -> pd.DataFrame:
    np.random.seed(42)
    lats = np.random.uniform(CITY_BOUNDS["lat_min"], CITY_BOUNDS["lat_max"], n_samples)
    lons = np.random.uniform(CITY_BOUNDS["lon_min"], CITY_BOUNDS["lon_max"], n_samples)
    districts = np.random.choice(DISTRICTS, n_samples)
    hours = np.random.randint(0, 24, n_samples)
    days = np.random.randint(0, 7, n_samples)
    is_weekend = (days >= 5).astype(int)

    lux_level = np.where(
        (hours >= 7) & (hours <= 19),
        np.random.uniform(150, 400, n_samples),
        np.random.uniform(2, 60, n_samples)
    )
    cctv_density = np.random.poisson(lam=4, size=n_samples)
    venue_density = np.random.poisson(lam=8, size=n_samples)
    transit_dist_m = np.random.exponential(scale=250, size=n_samples) + 20.0

    night_factor = np.exp(-((hours - 2) ** 2) / 18.0) * 35.0
    lighting_penalty = np.clip(100.0 - lux_level * 1.4, 0, 40.0)
    cctv_bonus = -np.clip(cctv_density * 3.0, 0, 25.0)
    venue_penalty = np.clip(venue_density * 2.2, 0, 30.0)

    district_bias = pd.Series(districts).map({
        "Halytskyi": 5.0,
        "Frankivskyi": -4.0,
        "Shevchenkivskyi": 2.0,
        "Lychakivskyi": -2.0,
        "Sykhivskyi": 4.0,
        "Zaliznychnyi": 3.0
    }).values

    noise = np.random.normal(0, 4.0, n_samples)
    risk_raw = 25.0 + night_factor + lighting_penalty + cctv_bonus + venue_penalty + district_bias + noise
    risk_score = np.clip(risk_raw, 0.0, 100.0).round(2)

    df = pd.DataFrame({
        "latitude": lats.round(6),
        "longitude": lons.round(6),
        "district": districts,
        "hour": hours,
        "day_of_week": days,
        "is_weekend": is_weekend,
        "lux_level": lux_level.round(1),
        "cctv_density": cctv_density,
        "venue_density": venue_density,
        "transit_dist_m": transit_dist_m.round(1),
        "risk_score": risk_score
    })

    df.to_csv(DATASET_PATH, index=False)
    print(f"Generated spatial dataset: {DATASET_PATH} ({n_samples} records)")
    return df

def generate_synthetic_graph() -> None:
    intersections = {
        "Node_0_0": {"name": "Stryiskyi Park / Naukova", "lat": 49.8058, "lon": 24.0175, "district": "Frankivskyi"},
        "Node_0_1": {"name": "Victoria Gardens / Kulparkivska", "lat": 49.8075, "lon": 23.9785, "district": "Frankivskyi"},
        "Node_0_2": {"name": "Lviv Polytechnic / Bandery St", "lat": 49.8355, "lon": 24.0144, "district": "Frankivskyi"},
        "Node_0_3": {"name": "Sakharova St / Kastelivka", "lat": 49.8265, "lon": 24.0160, "district": "Frankivskyi"},
        "Node_0_4": {"name": "Sykhiv / Dovzhenka Center", "lat": 49.7938, "lon": 24.0617, "district": "Sykhivskyi"},

        "Node_1_0": {"name": "Horodotska St / Levandivka", "lat": 49.8415, "lon": 23.9730, "district": "Zaliznychnyi"},
        "Node_1_1": {"name": "Main Railway Station", "lat": 49.8397, "lon": 23.9942, "district": "Zaliznychnyi"},
        "Node_1_2": {"name": "St. George Cathedral", "lat": 49.8385, "lon": 24.0132, "district": "Halytskyi"},
        "Node_1_3": {"name": "Stryiska St / Tax Office", "lat": 49.8180, "lon": 24.0225, "district": "Frankivskyi"},
        "Node_1_4": {"name": "Zelena St / Vodokanal", "lat": 49.8235, "lon": 24.0455, "district": "Lychakivskyi"},

        "Node_2_0": {"name": "Shevchenka St / Riasne", "lat": 49.8520, "lon": 23.9880, "district": "Shevchenkivskyi"},
        "Node_2_1": {"name": "Circus / Horodotska Hub", "lat": 49.8405, "lon": 24.0110, "district": "Halytskyi"},
        "Node_2_2": {"name": "Lviv Opera House / Svobody Ave", "lat": 49.8441, "lon": 24.0262, "district": "Halytskyi"},
        "Node_2_3": {"name": "Rynok Square / City Hall", "lat": 49.8419, "lon": 24.0315, "district": "Halytskyi"},
        "Node_2_4": {"name": "Lychakivska St / Medical Univ", "lat": 49.8369, "lon": 24.0512, "district": "Lychakivskyi"},

        "Node_3_0": {"name": "Kleparivska St / SKA Stadium", "lat": 49.8515, "lon": 24.0125, "district": "Shevchenkivskyi"},
        "Node_3_1": {"name": "Forum Lviv / Pid Dubom St", "lat": 49.8501, "lon": 24.0224, "district": "Shevchenkivskyi"},
        "Node_3_2": {"name": "Staryi Rynok / Pidzamche", "lat": 49.8483, "lon": 24.0310, "district": "Halytskyi"},
        "Node_3_3": {"name": "High Castle / Kryvonosa St", "lat": 49.8475, "lon": 24.0394, "district": "Halytskyi"},
        "Node_3_4": {"name": "Pasichna St / Pohulianka", "lat": 49.8270, "lon": 24.0680, "district": "Lychakivskyi"},

        "Node_4_0": {"name": "Chornovola Ave / North Hub", "lat": 49.8615, "lon": 24.0185, "district": "Shevchenkivskyi"},
        "Node_4_1": {"name": "Zamarstynivska / Spartak", "lat": 49.8685, "lon": 24.0290, "district": "Shevchenkivskyi"},
        "Node_4_2": {"name": "Pidzamche Railway Station", "lat": 49.8548, "lon": 24.0365, "district": "Shevchenkivskyi"},
        "Node_4_3": {"name": "Bohdana Khmelnytskoho St", "lat": 49.8575, "lon": 24.0450, "district": "Shevchenkivskyi"},
        "Node_4_4": {"name": "Trakt Hlynianskyi / Vynnyky", "lat": 49.8420, "lon": 24.0820, "district": "Lychakivskyi"}
    }

    edges = [
        ("Node_0_1", "Node_1_0"), ("Node_0_1", "Node_0_0"), ("Node_0_0", "Node_1_3"),
        ("Node_0_0", "Node_0_3"), ("Node_0_3", "Node_0_2"), ("Node_0_3", "Node_1_3"),
        ("Node_1_3", "Node_1_4"), ("Node_1_4", "Node_0_4"), ("Node_1_4", "Node_2_4"),
        ("Node_1_4", "Node_3_4"), ("Node_3_4", "Node_4_4"), ("Node_2_4", "Node_3_4"),
        ("Node_1_0", "Node_1_1"), ("Node_1_1", "Node_2_1"), ("Node_1_1", "Node_0_2"),
        ("Node_0_2", "Node_1_2"), ("Node_1_2", "Node_2_1"), ("Node_2_1", "Node_2_2"),
        ("Node_2_2", "Node_2_3"), ("Node_2_3", "Node_2_4"), ("Node_2_3", "Node_3_3"),
        ("Node_2_2", "Node_3_1"), ("Node_2_2", "Node_3_2"), ("Node_3_2", "Node_3_3"),
        ("Node_3_1", "Node_3_2"), ("Node_3_1", "Node_3_0"), ("Node_3_0", "Node_2_0"),
        ("Node_2_0", "Node_1_0"), ("Node_3_1", "Node_4_0"), ("Node_4_0", "Node_4_1"),
        ("Node_4_0", "Node_4_2"), ("Node_4_2", "Node_3_2"), ("Node_4_2", "Node_4_3"),
        ("Node_4_3", "Node_4_4"), ("Node_3_3", "Node_4_2"), ("Node_1_2", "Node_2_3")
    ]

    graph_data = {"nodes": intersections, "edges": edges}
    with open(ROAD_GRAPH_PATH, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2)
    print(f"Generated Lviv street network graph: {ROAD_GRAPH_PATH}")

if __name__ == "__main__":
    generate_spatial_dataset(5000)
    generate_synthetic_graph()