import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from api_client import SafetyAPIClient

st.set_page_config(
    page_title="Lviv Urban Safety Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #0F172A !important;
    }

    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        color: #0F172A !important;
        letter-spacing: -0.02em;
    }

    .stApp {
        background: linear-gradient(125deg, #FDFBFF 0%, #F4F6FF 45%, #F2FBF7 100%) !important;
        color: #0F172A !important;
    }

    header[data-testid="stHeader"] {
        background-color: rgba(253, 251, 255, 0.85) !important;
        backdrop-filter: blur(10px);
    }

    p, span, label, div, li, td, th {
        color: #0F172A;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8F7FF 100%) !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 18px !important;
        padding: 16px 18px !important;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04) !important;
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1.5px solid #E0E7FF !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.05) !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        border-color: #C4B5FD !important;
    }
    div[data-testid="stMetricLabel"] p {
        font-size: 0.74rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #475569 !important;
    }
    div[data-testid="stMetricValue"] div {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }

    .pastel-badge {
        display: inline-block;
        background: linear-gradient(90deg, #EDE9FE 0%, #E0E7FF 100%);
        color: #4C1D95 !important;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 999px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 8px;
        border: 1px solid #DDD6FE;
    }

    .status-pill {
        padding: 11px 18px;
        border-radius: 14px;
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 0.95rem;
        text-align: center;
        margin-bottom: 14px;
    }
    .status-safe {
        background: linear-gradient(90deg, #DCFCE7 0%, #D1FAE5 100%);
        color: #064E3B !important;
        border: 1.5px solid #6EE7B7;
    }
    .status-caution {
        background: linear-gradient(90deg, #FEF3C7 0%, #FFEDD5 100%);
        color: #78350F !important;
        border: 1.5px solid #FCD34D;
    }
    .status-alert {
        background: linear-gradient(90deg, #FFE4E6 0%, #FCE7F3 100%);
        color: #881337 !important;
        border: 1.5px solid #FDA4AF;
    }

    .stButton > button {
        background: linear-gradient(135deg, #EEF2FF 0%, #F3E8FF 100%) !important;
        color: #1E1B4B !important;
        border: 1.5px solid #C7D2FE !important;
        border-radius: 12px !important;
        padding: 0.55rem 1.2rem !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #E0E7FF 0%, #E9D5FF 100%) !important;
        border-color: #818CF8 !important;
        transform: translateY(-1px);
    }

    div[data-baseweb="input"],
    div[data-baseweb="select"] > div {
        background-color: #F8FAFC !important;
        border: 1.5px solid #DDD6FE !important;
        border-radius: 11px !important;
        color: #0F172A !important;
    }
    button[data-testid="stNumberInputStepDown"],
    button[data-testid="stNumberInputStepUp"] {
        background-color: #F3E8FF !important;
        color: #0F172A !important;
        border-left: 1px solid #DDD6FE !important;
    }
    ul[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
        border: 1px solid #DDD6FE !important;
        border-radius: 12px !important;
    }
    ul[data-baseweb="menu"] li {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }
    ul[data-baseweb="menu"] li:hover {
        background-color: #F3E8FF !important;
    }

    div[role="radiogroup"] {
        gap: 6px !important;
    }
    div[role="radiogroup"] label {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 6px 12px !important;
        transition: all 0.15s ease;
    }
    div[role="radiogroup"] label:hover {
        border-color: #A78BFA !important;
        background-color: #F5F3FF !important;
    }

    div[data-baseweb="slider"] div[role="slider"] {
        background: #7C3AED !important;
        border: 2px solid #FFFFFF !important;
        width: 16px !important;
        height: 16px !important;
    }
    div[data-baseweb="slider"] > div > div > div {
        background-color: #EDE9FE !important;
        height: 5px !important;
    }
    div[data-baseweb="slider"] > div > div > div > div {
        background: #8B5CF6 !important;
        height: 5px !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #FFFFFF !important;
        padding: 6px;
        border-radius: 16px;
        border: 1.5px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 11px;
        padding: 8px 16px;
        font-weight: 600;
        color: #334155 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #EDE9FE 0%, #E0E7FF 100%) !important;
        color: #3B0764 !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

client = SafetyAPIClient()

@st.cache_data(show_spinner=False)
def snap_route_to_roads(waypoints: tuple) -> tuple:
    """Snaps a sequence of (lat, lon) graph nodes to actual Lviv street geometry via OSRM."""
    try:
        coords_str = ";".join([f"{lon},{lat}" for lat, lon in waypoints])
        url = f"https://router.project-osrm.org/route/v1/foot/{coords_str}?overview=full&geometries=geojson"
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("routes"):
                geom = data["routes"][0]["geometry"]["coordinates"]
                lats = [pt[1] for pt in geom]
                lons = [pt[0] for pt in geom]
                return lats, lons
    except Exception:
        pass
    return [pt[0] for pt in waypoints], [pt[1] for pt in waypoints]

LVIV_PRESETS = {
    "Rynok Square (City Center)": (49.8419, 24.0315, "Halytskyi"),
    "Lviv Polytechnic / Bandery St": (49.8355, 24.0144, "Frankivskyi"),
    "Main Railway Station": (49.8397, 23.9942, "Zaliznychnyi"),
    "Sykhiv (Dovzhenka Center)": (49.7938, 24.0617, "Sykhivskyi"),
    "High Castle / Pidzamche": (49.8483, 24.0394, "Shevchenkivskyi"),
    "Lychakivska / Medical Univ": (49.8369, 24.0512, "Lychakivskyi"),
    "Custom Coordinates": (49.8400, 24.0300, "Halytskyi")
}

LVIV_ROUTE_NODES = {
    "Rynok Square / City Hall": "Node_2_3",
    "Lviv Opera House / Svobody Ave": "Node_2_2",
    "Lviv Polytechnic / Bandery St": "Node_0_2",
    "Main Railway Station": "Node_1_1",
    "Forum Lviv / Pid Dubom St": "Node_3_1",
    "High Castle / Kryvonosa St": "Node_3_3",
    "Lychakivska St / Medical Univ": "Node_2_4",
    "Sykhiv / Dovzhenka Center": "Node_0_4",
    "Victoria Gardens / Kulparkivska": "Node_0_1",
    "Stryiskyi Park / Naukova": "Node_0_0",
    "St. George Cathedral": "Node_1_2",
    "Circus / Horodotska Hub": "Node_2_1",
    "Staryi Rynok / Pidzamche": "Node_3_2",
    "Pidzamche Railway Station": "Node_4_2",
    "Chornovola Ave / North Hub": "Node_4_0",
    "Zamarstynivska / Spartak": "Node_4_1",
    "Zelena St / Vodokanal": "Node_1_4",
    "Pasichna St / Pohulianka": "Node_3_4",
    "Trakt Hlynianskyi / Vynnyky": "Node_4_4"
}

ROUTE_MODES = {
    "Maximum Safety Priority (Avoid High-Risk Zones)": 0.1,
    "Balanced Patrol Route (Safety + Speed)": 0.45,
    "Fastest Direct Path (Shortest Distance)": 0.95
}

MODEL_LABELS = {
    "stacking": "Stacking Meta-Ensemble (Consensus)",
    "lightgbm": "LightGBM Gradient Boosting",
    "random_forest": "Random Forest Regressor",
    "ridge": "Ridge Linear Baseline"
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

with st.sidebar:
    st.markdown('<div class="pastel-badge">Lviv Smart City Lab</div>', unsafe_allow_html=True)
    st.title("Urban Safety")
    st.caption("Spatio-Temporal Risk & Routing Intelligence")

    try:
        health = client.get_health()
        st.success(f"Backend Online ({len(health['available_models'])} models ready)")
    except Exception:
        st.error("Backend Offline (Run Uvicorn on :8000)")

    st.divider()

    st.markdown("**Active ML Architecture**")
    selected_model = st.selectbox(
        "Select inference model:",
        options=list(MODEL_LABELS.keys()),
        format_func=lambda x: MODEL_LABELS[x],
        key="global_model_selector"
    )
    st.caption("Switching models dynamically updates risk scores, path weights, and simulations.")

    st.divider()
    if st.button("Retrain All Ensemble Models", use_container_width=True):
        with st.spinner("Training models and updating artifacts..."):
            try:
                client.retrain()
                st.success("All models retrained.")
            except Exception as err:
                st.error(f"Error: {err}")


@st.fragment
def render_location_tab(active_model: str):
    st.markdown(f'<div class="pastel-badge">Active Model: {MODEL_LABELS[active_model]}</div>', unsafe_allow_html=True)
    st.subheader("Interactive Lviv Sector Risk Evaluation")

    col_ctrl, col_vis = st.columns([0.9, 2.1], gap="large")

    with col_ctrl:
        with st.container(border=True):
            st.markdown("**Location & Context**")
            preset_name = st.selectbox("Lviv Landmark Preset", list(LVIV_PRESETS.keys()), index=0)
            def_lat, def_lon, def_dist = LVIV_PRESETS[preset_name]

            districts = ["Halytskyi", "Frankivskyi", "Shevchenkivskyi", "Lychakivskyi", "Sykhivskyi", "Zaliznychnyi"]
            district = st.selectbox("Municipal District", districts, index=districts.index(def_dist))

            c1, c2 = st.columns(2)
            lat = c1.number_input("Latitude", 49.7700, 49.8900, def_lat, step=0.0005, format="%.4f")
            lon = c2.number_input("Longitude", 23.9400, 24.1100, def_lon, step=0.0005, format="%.4f")

            t1, t2 = st.columns(2)
            hour = t1.selectbox("Time of Day", list(range(24)), index=22, format_func=lambda h: f"{h:02d}:00")
            day_name = t2.selectbox("Day of Week", DAY_NAMES, index=4)
            day_of_week = DAY_NAMES.index(day_name)

            st.markdown("**Environment & Infrastructure**")
            i1, i2 = st.columns(2)
            lux = i1.number_input("Lighting (Lux)", 0.0, 500.0, 18.0, step=5.0)
            cctv = i2.number_input("CCTV Cameras", 0, 30, 3, step=1)

            i3, i4 = st.columns(2)
            venues = i3.number_input("Nightlife Venues", 0, 50, 9, step=1)
            transit_m = i4.number_input("Transit Dist (m)", 10.0, 3000.0, 140.0, step=20.0)

            compare_all = st.checkbox("Show all 4 models consensus", value=True)

    with col_vis:
        features = {
            "latitude": lat,
            "longitude": lon,
            "district": district,
            "hour": hour,
            "day_of_week": day_of_week,
            "is_weekend": 1 if day_of_week >= 5 else 0,
            "lux_level": lux,
            "cctv_density": cctv,
            "venue_density": venues,
            "transit_dist_m": transit_m
        }

        res = client.predict_safety(features, model_type=active_model)
        score = res["risk_score"]
        tier = res["safety_tier"]
        ci = res["confidence_interval"]

        tier_class = "status-safe" if tier == "Safe" else ("status-caution" if tier == "Caution" else "status-alert")
        st.markdown(f'<div class="status-pill {tier_class}">Classification: {tier.upper()} ({active_model.upper()})</div>', unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("Predicted Risk Index", f"{score} / 100")
        m2.metric("95% Confidence Range", f"{ci[0]} – {ci[1]}")
        m3.metric("Selected District", district)

        marker_color = "#10B981" if score < 35 else ("#F59E0B" if score < 65 else "#F43F5E")
        df_point = pd.DataFrame([{
            "lat": lat,
            "lon": lon,
            "label": f"{preset_name} | Risk: {score}"
        }])

        fig_map = px.scatter_map(
            df_point,
            lat="lat",
            lon="lon",
            hover_name="label",
            zoom=14.0,
            center={"lat": lat, "lon": lon},
            height=470
        )
        fig_map.update_traces(marker=dict(size=24, color=marker_color, opacity=0.92))
        fig_map.update_layout(
            map_style="carto-positron",
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig_map, use_container_width=True)

        if compare_all:
            comp_rows = []
            for m_key, m_label in MODEL_LABELS.items():
                r_m = client.predict_safety(features, model_type=m_key)
                comp_rows.append({"Model": m_label, "Risk Score": r_m["risk_score"]})
            df_comp = pd.DataFrame(comp_rows)

            fig_comp = px.bar(
                df_comp,
                x="Risk Score",
                y="Model",
                orientation="h",
                color="Risk Score",
                color_continuous_scale=["#A7F3D0", "#FDE68A", "#FECDD3"],
                range_x=[0, 108],
                text="Risk Score",
                title="Cross-Model Consensus for Current Location"
            )
            fig_comp.update_traces(textposition="outside", textfont=dict(color="#0F172A", size=12))
            fig_comp.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FAFAFA",
                font=dict(color="#0F172A"),
                xaxis=dict(title_font=dict(color="#0F172A"), tickfont=dict(color="#0F172A")),
                yaxis=dict(title="", tickfont=dict(color="#0F172A")),
                title_font=dict(color="#0F172A", size=14),
                height=220,
                margin=dict(l=10, r=25, t=38, b=10),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_comp, use_container_width=True)


@st.fragment
def render_routing_tab(active_model: str):
    st.markdown(f'<div class="pastel-badge">Routing Risk Estimator: {MODEL_LABELS[active_model]}</div>', unsafe_allow_html=True)
    st.subheader("Lviv Safe Path & Patrol Navigation Engine")

    col_left, col_right = st.columns([0.9, 2.1], gap="large")
    location_names = list(LVIV_ROUTE_NODES.keys())

    with col_left:
        with st.container(border=True):
            st.markdown("**Trip Waypoints**")
            start_label = st.selectbox("Starting Point (Origin)", location_names, index=0)
            end_label = st.selectbox("Destination Point", location_names, index=18)

            st.markdown("**Navigation Strategy**")
            route_strategy = st.radio(
                "Optimization Priority",
                options=list(ROUTE_MODES.keys()),
                index=0,
                label_visibility="collapsed"
            )
            alpha = ROUTE_MODES[route_strategy]

            st.caption(
                "Green trajectory snaps to Lviv streets while minimizing exposure to high-risk sectors. "
                "Red line shows the shortest direct path."
            )

    with col_right:
        start_node = LVIV_ROUTE_NODES[start_label]
        end_node = LVIV_ROUTE_NODES[end_label]

        if start_node == end_node:
            st.warning("Please select two different locations for origin and destination.")
        else:
            try:
                res_opt = client.get_safe_route(start_node, end_node, alpha=alpha, model_type=active_model)
                res_short = client.get_safe_route(start_node, end_node, alpha=1.0, model_type=active_model)

                dist_diff = ((res_opt["total_distance_m"] - res_short["total_distance_m"]) / max(1, res_short["total_distance_m"])) * 100.0
                risk_diff = ((res_short["average_risk"] - res_opt["average_risk"]) / max(1, res_short["average_risk"])) * 100.0

                r1, r2, r3 = st.columns(3)
                r1.metric("Route Distance", f"{res_opt['total_distance_m']} m", f"{dist_diff:+.1f}% vs shortest")
                r2.metric("Mean Sector Risk", f"{res_opt['average_risk']} / 100", f"{-risk_diff:+.1f}% threat", delta_color="inverse")
                r3.metric("Traversed Intersections", len(res_opt["path"]))

                df_opt = pd.DataFrame(res_opt["nodes_coords"])
                df_short = pd.DataFrame(res_short["nodes_coords"])

                inv_nodes = {v: k for k, v in LVIV_ROUTE_NODES.items()}
                df_opt["label"] = df_opt["node"].map(lambda n: inv_nodes.get(n, n)) if "node" in df_opt.columns else [f"Step {i+1}" for i in range(len(df_opt))]
                df_short["label"] = df_short["node"].map(lambda n: inv_nodes.get(n, n)) if "node" in df_short.columns else [f"Step {i+1}" for i in range(len(df_short))]

                opt_waypoints = tuple(zip(df_opt["lat"], df_opt["lon"]))
                short_waypoints = tuple(zip(df_short["lat"], df_short["lon"]))

                opt_road_lats, opt_road_lons = snap_route_to_roads(opt_waypoints)
                short_road_lats, short_road_lons = snap_route_to_roads(short_waypoints)

                fig_route_map = go.Figure()

                fig_route_map.add_trace(go.Scattermap(
                    lat=short_road_lats,
                    lon=short_road_lons,
                    mode="lines",
                    name="Shortest Street Path",
                    line=dict(width=4, color="#F43F5E")
                ))

                fig_route_map.add_trace(go.Scattermap(
                    lat=opt_road_lats,
                    lon=opt_road_lons,
                    mode="lines",
                    name="Recommended Safe Route",
                    line=dict(width=6, color="#10B981")
                ))

                fig_route_map.add_trace(go.Scattermap(
                    lat=df_opt["lat"],
                    lon=df_opt["lon"],
                    mode="markers",
                    name="Safe Waypoints",
                    marker=dict(size=11, color="#059669"),
                    text=df_opt["label"] + " (Risk: " + df_opt["risk"].astype(str) + ")",
                    hoverinfo="text"
                ))

                center_lat = (df_opt["lat"].iloc[0] + df_opt["lat"].iloc[-1]) / 2
                center_lon = (df_opt["lon"].iloc[0] + df_opt["lon"].iloc[-1]) / 2

                fig_route_map.update_layout(
                    map=dict(
                        style="carto-positron",
                        center=dict(lat=center_lat, lon=center_lon),
                        zoom=13.0
                    ),
                    font=dict(color="#0F172A"),
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=580,
                    legend=dict(
                        yanchor="top", y=0.98,
                        xanchor="left", x=0.02,
                        bgcolor="rgba(255, 255, 255, 0.94)",
                        font=dict(color="#0F172A", size=12)
                    )
                )
                st.plotly_chart(fig_route_map, use_container_width=True)

                st.markdown("#### Segment-by-Segment Risk Profile Along Route")
                fig_profile = go.Figure()
                fig_profile.add_trace(go.Scatter(
                    x=list(range(1, len(df_short) + 1)),
                    y=df_short["risk"],
                    mode="lines+markers",
                    name="Shortest Path Risk",
                    text=df_short["label"],
                    hovertemplate="%{text}<br>Risk: %{y}/100<extra></extra>",
                    line=dict(color="#F43F5E", width=3, dash="dash"),
                    marker=dict(size=8)
                ))
                fig_profile.add_trace(go.Scatter(
                    x=list(range(1, len(df_opt) + 1)),
                    y=df_opt["risk"],
                    mode="lines+markers",
                    name="Safe Route Risk",
                    text=df_opt["label"],
                    hovertemplate="%{text}<br>Risk: %{y}/100<extra></extra>",
                    line=dict(color="#10B981", width=4),
                    marker=dict(size=10)
                ))
                fig_profile.update_layout(
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#F8FAFC",
                    font=dict(color="#0F172A"),
                    yaxis=dict(title="Sector Risk Score (0-100)", range=[0, 100], tickfont=dict(color="#0F172A")),
                    xaxis=dict(title="Route Waypoint Step", dtick=1, tickfont=dict(color="#0F172A")),
                    height=290,
                    margin=dict(l=20, r=20, t=20, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_profile, use_container_width=True)

            except Exception as e:
                st.error(f"Routing backend error: {e}")


@st.fragment
def render_hotspots_tab():
    st.markdown('<div class="pastel-badge">Unsupervised Haversine DBSCAN Clustering</div>', unsafe_allow_html=True)
    st.subheader("Lviv Spatio-Temporal Incident Hotspots")

    col_left, col_right = st.columns([0.9, 2.1], gap="large")

    with col_left:
        with st.container(border=True):
            st.markdown("**DBSCAN Cluster Parameters**")
            hour_slot = st.selectbox("Monitoring Time Slot", list(range(24)), index=23, format_func=lambda h: f"{h:02d}:00 – {h:02d}:59")
            eps = st.select_slider("Search Radius Epsilon (m)", options=[150, 250, 350, 450, 600, 800, 1000], value=450)
            min_pts = st.select_slider("Minimum Events per Cluster", options=[3, 4, 5, 7, 10, 12], value=5)
            st.caption("Clusters represent high-density incident zones detected automatically without prior labels.")

    with col_right:
        res_hs = client.get_hotspots(hour=hour_slot, eps_meters=float(eps), min_samples=int(min_pts))
        st.metric("Identified High-Density Clusters in Lviv", res_hs["hotspots_found"])

        if res_hs["clusters"]:
            df_cl = pd.DataFrame(res_hs["clusters"])
            fig_hs = px.scatter_map(
                df_cl,
                lat="center_lat",
                lon="center_lon",
                size="points_count",
                color="avg_risk",
                color_continuous_scale=["#FDE68A", "#FDBA74", "#FDA4AF"],
                size_max=34,
                zoom=12.0,
                center={"lat": 49.835, "lon": 24.025},
                hover_name="cluster_id",
                hover_data={"points_count": True, "avg_risk": True},
                height=540
            )
            fig_hs.update_layout(
                map_style="carto-positron",
                font=dict(color="#0F172A"),
                margin=dict(l=0, r=0, t=0, b=0)
            )
            st.plotly_chart(fig_hs, use_container_width=True)
            st.dataframe(df_cl, use_container_width=True, hide_index=True)
        else:
            st.info("No critical clusters detected for the selected time window and radius.")


@st.fragment
def render_whatif_tab(active_model: str):
    st.markdown(f'<div class="pastel-badge">Counterfactual Engine: {MODEL_LABELS[active_model]}</div>', unsafe_allow_html=True)
    st.subheader("Municipal Infrastructure Upgrade Simulator")

    col_left, col_right = st.columns([0.9, 2.1], gap="large")

    with col_left:
        with st.container(border=True):
            st.markdown("**Current Baseline Conditions**")
            b1, b2 = st.columns(2)
            base_lux = b1.number_input("Current Lux", 0.0, 40.0, 5.0, step=2.0)
            base_cctv = b2.number_input("Current CCTV", 0, 5, 0, step=1)

            st.markdown("**Proposed Upgrades**")
            u1, u2 = st.columns(2)
            add_lux = u1.number_input("Add Lighting (+Lux)", 0.0, 150.0, 40.0, step=5.0)
            add_cctv = u2.number_input("Add Cameras (+CCTV)", 0, 15, 3, step=1)
            st.caption("Simulates risk score reduction for a high-risk nightlife zone in Halytskyi district at 23:00.")

    with col_right:
        base_f = {
            "latitude": 49.8419,
            "longitude": 24.0315,
            "district": "Halytskyi",
            "hour": 23,
            "day_of_week": 5,
            "is_weekend": 1,
            "lux_level": base_lux,
            "cctv_density": base_cctv,
            "venue_density": 15,
            "transit_dist_m": 180.0
        }
        base_score = client.predict_safety(base_f, active_model)["risk_score"]

        f_lux = base_f.copy()
        f_lux["lux_level"] += add_lux
        score_lux = client.predict_safety(f_lux, active_model)["risk_score"]
        delta_lux = round(score_lux - base_score, 2)

        f_both = f_lux.copy()
        f_both["cctv_density"] += add_cctv
        final_score = client.predict_safety(f_both, active_model)["risk_score"]
        delta_cctv = round(final_score - score_lux, 2)

        s1, s2, s3 = st.columns(3)
        s1.metric("Baseline Sector Risk", f"{base_score} / 100")
        s2.metric("Post-Upgrade Risk", f"{final_score} / 100", f"{round(final_score - base_score, 2):+.2f} pts", delta_color="inverse")
        s3.metric("Total Safety Gain", f"+{abs(round(final_score - base_score, 2))} pts")

        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["Baseline Risk", "Lighting Upgrade", "CCTV Deployment", "Target Risk"],
            textposition="outside",
            textfont=dict(color="#0F172A", size=13),
            text=[f"{base_score:.1f}", f"{delta_lux:+.1f}", f"{delta_cctv:+.1f}", f"{final_score:.1f}"],
            y=[base_score, delta_lux, delta_cctv, 0],
            connector={"line": {"color": "#CBD5E1"}},
            decreasing={"marker": {"color": "#6EE7B7"}},
            increasing={"marker": {"color": "#FDA4AF"}},
            totals={"marker": {"color": "#A5B4FC"}}
        ))
        fig_wf.update_layout(
            title=dict(text="Risk Reduction Waterfall Bridge", font=dict(color="#0F172A")),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#F8FAFC",
            font=dict(color="#0F172A"),
            xaxis=dict(tickfont=dict(color="#0F172A")),
            yaxis=dict(tickfont=dict(color="#0F172A")),
            height=480,
            margin=dict(l=20, r=20, t=45, b=20)
        )
        st.plotly_chart(fig_wf, use_container_width=True)


@st.fragment
def render_benchmark_tab(active_model: str):
    st.markdown(f'<div class="pastel-badge">Batch Inference Model: {MODEL_LABELS[active_model]}</div>', unsafe_allow_html=True)
    st.subheader("Multi-Model Validation Metrics & Batch Patrol Audit")

    bench = client.get_benchmark()
    df_bench = pd.DataFrame(bench["metrics"]).T
    df_bench.index.name = "Model Architecture"

    st.dataframe(
        df_bench.style.highlight_max(subset=["r2"], color="#DCFCE7").highlight_min(
            subset=["mae", "rmse", "latency_per_sample_ms"], color="#DCFCE7"
        ),
        use_container_width=True
    )

    c1, c2 = st.columns(2, gap="large")
    with c1:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=df_bench.index, y=df_bench["r2"], name="R-Squared", marker_color="#A7F3D0"))
        fig_bar.add_trace(go.Bar(x=df_bench.index, y=df_bench["rmse"], name="RMSE", marker_color="#FECDD3"))
        fig_bar.update_layout(
            barmode="group",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#F8FAFC",
            font=dict(color="#0F172A"),
            xaxis=dict(tickfont=dict(color="#0F172A")),
            yaxis=dict(tickfont=dict(color="#0F172A")),
            legend=dict(font=dict(color="#0F172A")),
            title=dict(text="Model Determination (R2) vs Error (RMSE)", font=dict(color="#0F172A")),
            height=360
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        imp_data = bench.get("feature_importance", {})
        if imp_data:
            df_imp = pd.DataFrame(list(imp_data.items()), columns=["Feature", "Importance (%)"])
            fig_imp = px.bar(
                df_imp,
                x="Importance (%)",
                y="Feature",
                orientation="h",
                title="Feature Contribution (%)",
                color="Importance (%)",
                color_continuous_scale=["#DDD6FE", "#8B5CF6"]
            )
            fig_imp.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#F8FAFC",
                font=dict(color="#0F172A"),
                xaxis=dict(tickfont=dict(color="#0F172A"), title_font=dict(color="#0F172A")),
                yaxis=dict(categoryorder="total ascending", tickfont=dict(color="#0F172A"), title=""),
                title_font=dict(color="#0F172A"),
                height=360,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_imp, use_container_width=True)

    st.divider()
    st.subheader("Batch Patrol Audit on Lviv Map")
    uploaded_file = st.file_uploader("Upload Patrol Points CSV", type=["csv"])
    if uploaded_file:
        df_upload = pd.read_csv(uploaded_file)
        req_cols = [
            "latitude", "longitude", "district", "hour", "day_of_week",
            "lux_level", "cctv_density", "venue_density", "transit_dist_m", "is_weekend"
        ]
        records = df_upload[req_cols].to_dict(orient="records")
        res_batch = client.predict_batch(records, model_type=active_model)
        df_upload["predicted_risk"] = [p["risk_score"] for p in res_batch["predictions"]]

        b1, b2 = st.columns(2)
        b1.metric("Audited Locations", res_batch["count"])
        b2.metric("Mean Risk Index", f"{res_batch['mean_risk_score']} / 100")

        fig_batch_map = px.scatter_map(
            df_upload,
            lat="latitude",
            lon="longitude",
            color="predicted_risk",
            color_continuous_scale=["#6EE7B7", "#FDE68A", "#FDA4AF"],
            zoom=11.8,
            center={"lat": 49.835, "lon": 24.025},
            height=540
        )
        fig_batch_map.update_layout(
            map_style="carto-positron",
            font=dict(color="#0F172A"),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig_batch_map, use_container_width=True)

        st.download_button(
            "Download Audited CSV",
            df_upload.to_csv(index=False),
            "lviv_audited_points.csv",
            mime="text/csv"
        )

tab_eval, tab_route, tab_hotspots, tab_whatif, tab_bench = st.tabs([
    "1. Lviv Location Assessment",
    "2. Safe Path Routing",
    "3. Hotspot Discovery (DBSCAN)",
    "4. What-If Infrastructure",
    "5. Model Benchmark & Batch Audit"
])

with tab_eval:
    render_location_tab(selected_model)
with tab_route:
    render_routing_tab(selected_model)
with tab_hotspots:
    render_hotspots_tab()
with tab_whatif:
    render_whatif_tab(selected_model)
with tab_bench:
    render_benchmark_tab(selected_model)