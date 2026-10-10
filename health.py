"""Core logic: data simulator, health score and status rules.
Kept separate from the dashboard so it is easy to test and explain."""
import numpy as np
import pandas as pd

# (warning, critical) limits. Illustrative values - tune for your machine.
DEFAULT_LIMITS = {
    "temperature": (60.0, 80.0),   # degrees C
    "vibration":   (4.0, 7.0),     # mm/s RMS
    "sound":       (75.0, 90.0),   # dB
}
WEIGHTS = {"temperature": 0.35, "vibration": 0.40, "sound": 0.25}

SCENARIOS = ["Normal", "Overheating", "Bearing wear", "Imbalance", "Potential failure"]

# Target level each parameter drifts toward in each scenario
_TARGETS = {
    "Normal":            {"temperature": 45, "vibration": 2.0, "sound": 62},
    "Overheating":       {"temperature": 72, "vibration": 2.5, "sound": 64},
    "Bearing wear":      {"temperature": 58, "vibration": 5.5, "sound": 80},
    "Imbalance":         {"temperature": 50, "vibration": 6.0, "sound": 70},
    "Potential failure": {"temperature": 85, "vibration": 8.0, "sound": 93},
}


def simulate_next(prev, scenario, rng):
    """Next simulated reading: drifts toward the scenario level, plus noise."""
    tgt = _TARGETS[scenario]
    noise = {"temperature": 0.8, "vibration": 0.25, "sound": 1.5}
    out = {}
    for k in tgt:
        p = prev[k] if prev else _TARGETS["Normal"][k]
        out[k] = max(0.0, p + 0.12 * (tgt[k] - p) + rng.normal(0, noise[k]))
    return out


def param_status(name, value, limits):
    warn, crit = limits[name]
    if value >= crit:
        return "Critical"
    if value >= warn:
        return "Warning"
    return "Normal"


def health_score(reading, limits):
    """100 = perfectly healthy, 0 = every parameter at/over critical.
    Penalty per parameter ramps from 0 at 'warning * 0.6' up to 1 at 'critical'."""
    penalty = 0.0
    for k, v in reading.items():
        warn, crit = limits[k]
        start = warn * 0.8
        p = min(max((v - start) / (crit - start), 0.0), 1.0)
        penalty += WEIGHTS[k] * p
    return round(100 * (1 - penalty), 1)


def overall_status(reading, limits):
    """Returns (status, message, colour)."""
    st = {k: param_status(k, v, limits) for k, v in reading.items()}
    flagged = [k for k, s in st.items() if s != "Normal"]
    any_crit = any(s == "Critical" for s in st.values())
    if not flagged:
        return "Healthy", "Machine operating normally.", "green"
    if len(flagged) >= 2:
        return ("Potential failure",
                "INSPECTION REQUIRED: " + ", ".join(flagged) + " abnormal.", "red")
    k = flagged[0]
    msg = {
        "temperature": "Temperature warning: check cooling / load.",
        "vibration": "Vibration warning: check bearings / mounting / balance.",
        "sound": "Sound warning: check for friction or loose parts.",
    }[k]
    return ("Critical " + k if st[k] == "Critical" else "Warning"), msg, \
        ("red" if st[k] == "Critical" else "orange")


def rising_trend(series, window=15):
    """True if the last `window` points show a clear upward slope."""
    s = np.asarray(series[-window:], dtype=float)
    if len(s) < window:
        return False
    slope = np.polyfit(np.arange(len(s)), s, 1)[0]
    return slope > 0.02 * max(abs(s.mean()), 1e-6)
