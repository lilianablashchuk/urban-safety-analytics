import joblib
import json
import time
from datetime import datetime
import numpy as np
import pandas as pd
import networkx as nx
from geopy.distance import geodesic
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.cluster import DBSCAN
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error
import lightgbm as lgb

from api.config import DATASET_PATH, MODEL_BUNDLE_PATH, ROAD_GRAPH_PATH

CATEGORICAL_FEATURES = ["district"]
NUMERICAL_FEATURES = [
    "latitude", "longitude", "hour", "day_of_week",
    "is_weekend", "lux_level", "cctv_density",
    "venue_density", "transit_dist_m"
]

class SafetyModelService:
    def __init__(self):
        self.bundle = None
        self.graph_nodes = {}
        self.graph_edges = []
        self.load_graph()
        self.load_or_train()

    def load_graph(self) -> None:
        if ROAD_GRAPH_PATH.exists():
            with open(ROAD_GRAPH_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.graph_nodes = data["nodes"]
            self.graph_edges = data["edges"]

    def load_or_train(self) -> None:
        if MODEL_BUNDLE_PATH.exists():
            self.bundle = joblib.load(MODEL_BUNDLE_PATH)
        else:
            self.train_all_models()

    def _build_preprocessor(self) -> ColumnTransformer:
        return ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), NUMERICAL_FEATURES),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES)
            ]
        )

    def train_all_models(self) -> dict:
        if not DATASET_PATH.exists() or not ROAD_GRAPH_PATH.exists():
            from scripts.generate_dataset import generate_spatial_dataset, generate_synthetic_graph
            generate_spatial_dataset(5000)
            generate_synthetic_graph()
            self.load_graph()

        df = pd.read_csv(DATASET_PATH)
        X = df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
        y = df["risk_score"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        ridge_pipe = Pipeline([
            ("preprocessor", self._build_preprocessor()),
            ("regressor", Ridge(alpha=1.0))
        ])

        rf_pipe = Pipeline([
            ("preprocessor", self._build_preprocessor()),
            ("regressor", RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1))
        ])

        lgb_pipe = Pipeline([
            ("preprocessor", self._build_preprocessor()),
            ("regressor", lgb.LGBMRegressor(n_estimators=150, learning_rate=0.05, num_leaves=31, random_state=42, verbose=-1))
        ])

        estimators = [
            ("ridge", Ridge(alpha=1.0)),
            ("rf", RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)),
            ("lgbm", lgb.LGBMRegressor(n_estimators=80, learning_rate=0.05, num_leaves=25, random_state=42, verbose=-1))
        ]
        stacking_pipe = Pipeline([
            ("preprocessor", self._build_preprocessor()),
            ("regressor", StackingRegressor(estimators=estimators, final_estimator=Ridge(alpha=0.5), cv=3))
        ])

        models = {
            "ridge": ridge_pipe,
            "random_forest": rf_pipe,
            "lightgbm": lgb_pipe,
            "stacking": stacking_pipe
        }

        metrics = {}
        for name, pipe in models.items():
            t0 = time.time()
            pipe.fit(X_train, y_train)
            fit_time = round(time.time() - t0, 3)

            t0 = time.time()
            y_pred = pipe.predict(X_test)
            latency_ms = round(((time.time() - t0) / len(X_test)) * 1000, 3)

            metrics[name] = {
                "r2": round(float(r2_score(y_test, y_pred)), 4),
                "mae": round(float(mean_absolute_error(y_test, y_pred)), 3),
                "rmse": round(float(root_mean_squared_error(y_test, y_pred)), 3),
                "fit_time_sec": fit_time,
                "latency_per_sample_ms": latency_ms
            }

        rf_reg = rf_pipe.named_steps["regressor"]
        preprocessor = rf_pipe.named_steps["preprocessor"]
        cat_names = list(preprocessor.named_transformers_["cat"].get_feature_names_out(CATEGORICAL_FEATURES))
        all_feature_names = NUMERICAL_FEATURES + cat_names
        raw_importances = rf_reg.feature_importances_

        grouped_imp = {}
        for fname, imp in zip(all_feature_names, raw_importances):
            base_name = "district" if fname.startswith("district_") else fname
            grouped_imp[base_name] = grouped_imp.get(base_name, 0.0) + float(imp)
        grouped_imp = {k: round(v * 100.0, 2) for k, v in sorted(grouped_imp.items(), key=lambda x: x[1], reverse=True)}

        self.bundle = {
            "models": models,
            "metrics": metrics,
            "feature_importance": grouped_imp,
            "trained_at": datetime.now().isoformat(),
            "total_samples": len(df)
        }
        joblib.dump(self.bundle, MODEL_BUNDLE_PATH)
        return self.bundle

    def predict(self, features_dict: dict, model_type: str = "stacking") -> dict:
        if not self.bundle:
            raise ValueError("Model bundle is not initialized.")
        model = self.bundle["models"].get(model_type, self.bundle["models"]["stacking"])
        df_in = pd.DataFrame([features_dict])
        pred = float(np.clip(model.predict(df_in)[0], 0.0, 100.0))

        tier = "Safe" if pred < 35.0 else ("Caution" if pred < 65.0 else "High Alert")
        mae = self.bundle["metrics"].get(model_type, self.bundle["metrics"]["stacking"])["mae"]
        ci = [round(max(0.0, pred - 1.96 * mae), 2), round(min(100.0, pred + 1.96 * mae), 2)]

        return {
            "risk_score": round(pred, 2),
            "safety_tier": tier,
            "confidence_interval": ci,
            "model_used": model_type
        }

    def predict_batch(self, items: list, model_type: str = "stacking") -> dict:
        if not self.bundle:
            raise ValueError("Model bundle is not initialized.")
        model = self.bundle["models"].get(model_type, self.bundle["models"]["stacking"])
        df_in = pd.DataFrame(items)
        preds = np.clip(model.predict(df_in), 0.0, 100.0).round(2)
        res = [{"index": i, "risk_score": float(p)} for i, p in enumerate(preds)]
        return {
            "count": len(res),
            "predictions": res,
            "mean_risk_score": round(float(np.mean(preds)), 2)
        }

    def find_hotspots(self, hour: int, eps_meters: float = 350.0, min_samples: int = 5) -> dict:
        df = pd.read_csv(DATASET_PATH)
        sub = df[(df["hour"] == hour) & (df["risk_score"] >= 45.0)].copy()
        if len(sub) < min_samples:
            return {"hotspots_found": 0, "clusters": []}

        earth_radius_m = 6371000.0
        epsilon_rad = eps_meters / earth_radius_m

        coords = np.radians(sub[["latitude", "longitude"]].values)
        db = DBSCAN(eps=epsilon_rad, min_samples=min_samples, metric="haversine")
        sub["cluster"] = db.fit_predict(coords)

        clusters = []
        for cid in sorted(sub["cluster"].unique()):
            if cid == -1:
                continue
            c_points = sub[sub["cluster"] == cid]
            clusters.append({
                "cluster_id": int(cid),
                "center_lat": round(float(c_points["latitude"].mean()), 6),
                "center_lon": round(float(c_points["longitude"].mean()), 6),
                "points_count": int(len(c_points)),
                "avg_risk": round(float(c_points["risk_score"].mean()), 2)
            })

        return {"hotspots_found": len(clusters), "clusters": clusters}

    def calculate_safe_route(self, start_node: str, end_node: str, alpha: float = 0.5, model_type: str = "stacking") -> dict:
        if start_node not in self.graph_nodes or end_node not in self.graph_nodes:
            raise ValueError("Invalid start or end node identifier.")

        node_ids = list(self.graph_nodes.keys())
        node_features = [
            {
                "latitude": self.graph_nodes[nid]["lat"],
                "longitude": self.graph_nodes[nid]["lon"],
                "district": self.graph_nodes[nid]["district"],
                "hour": 22,
                "day_of_week": 4,
                "is_weekend": 0,
                "lux_level": 15.0,
                "cctv_density": 2,
                "venue_density": 12 if self.graph_nodes[nid]["district"] in ["Halytskyi", "Sykhivskyi"] else 3,
                "transit_dist_m": 120.0
            }
            for nid in node_ids
        ]
        batch_res = self.predict_batch(node_features, model_type=model_type)
        node_risks = {nid: pred["risk_score"] for nid, pred in zip(node_ids, batch_res["predictions"])}

        G = nx.Graph()
        for u, v in self.graph_edges:
            coord_u = (self.graph_nodes[u]["lat"], self.graph_nodes[u]["lon"])
            coord_v = (self.graph_nodes[v]["lat"], self.graph_nodes[v]["lon"])
            dist_m = geodesic(coord_u, coord_v).meters
            edge_risk = (node_risks[u] + node_risks[v]) / 2.0

            cost = alpha * dist_m + (1.0 - alpha) * (edge_risk * 15.0)
            G.add_edge(u, v, weight=cost, distance=dist_m, risk=edge_risk)

        path = nx.shortest_path(G, source=start_node, target=end_node, weight="weight")

        total_dist = 0.0
        total_risk = 0.0
        coords = []
        for i in range(len(path) - 1):
            e_data = G.get_edge_data(path[i], path[i + 1])
            total_dist += e_data["distance"]
            total_risk += e_data["risk"]
            coords.append({
                "node": path[i],
                "name": self.graph_nodes[path[i]].get("name", path[i]),
                "lat": self.graph_nodes[path[i]]["lat"],
                "lon": self.graph_nodes[path[i]]["lon"],
                "risk": round(node_risks[path[i]], 1)
            })

        last = path[-1]
        coords.append({
            "node": last,
            "name": self.graph_nodes[last].get("name", last),
            "lat": self.graph_nodes[last]["lat"],
            "lon": self.graph_nodes[last]["lon"],
            "risk": round(node_risks[last], 1)
        })

        avg_risk = round(total_risk / max(1, len(path) - 1), 2)
        return {
            "path": path,
            "total_distance_m": round(total_dist, 1),
            "average_risk": avg_risk,
            "integrated_cost": round(alpha * total_dist + (1.0 - alpha) * (avg_risk * 15.0), 2),
            "nodes_coords": coords
        }

model_service = SafetyModelService()