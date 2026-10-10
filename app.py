"""Machine Health Monitoring & Early-Failure Warning - software prototype.
Run:  streamlit run app.py
Data is SIMULATED (or loaded from a CSV). It is not a real sensor measurement."""
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime
from health import (DEFAULT_LIMITS, SCENARIOS, simulate_next, param_status,
                    health_score, overall_status, rising_trend)

st.set_page_config(page_title="Machine Health Monitor", page_icon="🏭", layout="wide")
st.title("🏭 Machine Health Monitoring & Early Failure Warning")
st.caption("Prototype using simulated temperature, vibration and sound data.")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Settings")
    source = st.radio("Data source", ["Simulation", "Upload CSV"])
    st.subheader("Thresholds (warning / critical)")
    limits = {}
    t = DEFAULT_LIMITS["temperature"]; v = DEFAULT_LIMITS["vibration"]; s = DEFAULT_LIMITS["sound"]
    limits["temperature"] = st.slider("Temperature (°C)", 20.0, 120.0, t)
    limits["vibration"] = st.slider("Vibration (mm/s)", 0.0, 15.0, v)
    limits["sound"] = st.slider("Sound (dB)", 40.0, 120.0, s)

UNITS = {"temperature": "°C", "vibration": "mm/s", "sound": "dB"}
ICON = {"Normal": "🟢", "Warning": "🟠", "Critical": "🔴"}


def show(df):
    """Render the dashboard for a dataframe with temperature/vibration/sound."""
    last = df.iloc[-1][["temperature", "vibration", "sound"]].to_dict()
    score = health_score(last, limits)
    status, msg, colour = overall_status(last, limits)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Health score", f"{score} / 100")
    for col, k in zip((c2, c3, c4), ("temperature", "vibration", "sound")):
        col.metric(f"{ICON[param_status(k, last[k], limits)]} {k.title()}",
                   f"{last[k]:.1f} {UNITS[k]}",
                   param_status(k, last[k], limits), delta_color="off")

    box = {"green": st.success, "orange": st.warning, "red": st.error}[colour]
    box(f"**{status}** - {msg}")
    for k in ("temperature", "vibration", "sound"):
        if rising_trend(df[k].tolist()) and param_status(k, last[k], limits) == "Normal":
            st.info(f"Early warning: {k} is trending upward.")

    g1, g2, g3 = st.columns(3)
    for col, k in zip((g1, g2, g3), ("temperature", "vibration", "sound")):
        col.subheader(f"{k.title()} ({UNITS[k]})")
        col.line_chart(df.set_index("time")[k], height=220)

    with st.expander("Recorded data"):
        st.dataframe(df.tail(100), width="stretch")
        st.download_button("Download CSV", df.to_csv(index=False), "sensor_log.csv")


if source == "Simulation":
    with st.sidebar:
        scenario = st.selectbox("Machine condition (demo)", SCENARIOS)
        speed = st.slider("Update every (s)", 0.5, 3.0, 1.0)
        if st.button("Reset data"):
            st.session_state.pop("data", None)

    if "rng" not in st.session_state:
        st.session_state.rng = np.random.default_rng(42)
        st.session_state.data = []

    @st.fragment(run_every=speed)
    def live():
        data = st.session_state.data
        prev = {k: data[-1][k] for k in ("temperature", "vibration", "sound")} if data else None
        r = simulate_next(prev, scenario, st.session_state.rng)
        r["time"] = datetime.now().strftime("%H:%M:%S")
        data.append(r)
        del data[:-300]
        show(pd.DataFrame(data))

    live()
else:
    f = st.file_uploader("CSV with columns: time, temperature, vibration, sound", type="csv")
    if f:
        df = pd.read_csv(f)
        if {"temperature", "vibration", "sound"} <= set(df.columns):
            if "time" not in df.columns:
                df["time"] = range(len(df))
            show(df)
        else:
            st.error("CSV must contain temperature, vibration and sound columns.")
    else:
        st.info("Upload a CSV (for example sensor_log.csv from the logger).")
