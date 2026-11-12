# Urban Safety Analytics & Safe Routing Platform

![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=flat&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-FF4B4B?style=flat&logo=streamlit)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4.0-F7931E?style=flat&logo=scikit-learn)
![LightGBM](https://img.shields.io/badge/LightGBM-4.3.0-brightgreen?style=flat)
![Tests](https://img.shields.io/badge/Pytest-Passing-success?style=flat&logo=pytest)

A distributed Machine Learning platform designed for municipal situational safety centers, patrol dispatching, and civilian navigation. The platform predicts spatio-temporal risk scores, discovers density-based incident hotspots (DBSCAN), simulates counterfactual infrastructure interventions, and computes safety-weighted shortest paths using Dijkstra's algorithm.

---

### System Architecture

```mermaid
graph TD
    subgraph Client [Client Layer: Streamlit :8501]
        UI[Analytical Geo-Terminal UI]
        APIClient[SafetyAPIClient]
        UI --> APIClient
    end

    subgraph Server [Server Layer: FastAPI :8000]
        Router[REST Endpoints]
        Validator[Pydantic v2 Validation]
        Service[SafetyModelService]
        Router --> Validator --> Service
    end

    subgraph Core [ML Pipeline & Graph Core]
        Pipe[ColumnTransformer Pipeline]
        Models[Ridge | Random Forest | LightGBM | Stacking]
        Graph[NetworkX Safe Routing]
        Cluster[DBSCAN Hotspot Clustering]
        Storage[(Artifact Bundle .joblib)]

        Service --> Pipe --> Models
        Service --> Graph
        Service --> Cluster
        Service <--> Storage
    end

    APIClient -->|HTTP REST / JSON| Router