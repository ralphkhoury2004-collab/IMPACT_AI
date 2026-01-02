# backend/app/ai_infer.py
import os
import numpy as np
import pandas as pd
import joblib

# backend/app/ai_infer.py -> go up to backend/
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # .../backend
MODELS_DIR = os.path.join(BASE_DIR, "models")

CRASH_MODEL_PATH = os.path.join(MODELS_DIR, "crash_detector.joblib")
SEV_MODEL_PATH   = os.path.join(MODELS_DIR, "severity_model.joblib")

_crash_model = None
_sev_model = None

def load_models():
    """Load models once (cached)."""
    global _crash_model, _sev_model

    if not os.path.exists(CRASH_MODEL_PATH):
        raise FileNotFoundError(f"Missing model: {CRASH_MODEL_PATH}")
    if not os.path.exists(SEV_MODEL_PATH):
        raise FileNotFoundError(f"Missing model: {SEV_MODEL_PATH}")

    if _crash_model is None:
        _crash_model = joblib.load(CRASH_MODEL_PATH)

    if _sev_model is None:
        _sev_model = joblib.load(SEV_MODEL_PATH)

def _crash_features(df: pd.DataFrame) -> np.ndarray:
    # accel magnitude
    a_mag = np.sqrt(df["ax"]**2 + df["ay"]**2 + df["az"]**2)

    # dt
    dt = float(np.mean(np.diff(df["t"])))
    if dt <= 0:
        dt = 1e-3

    # jerk
    jerk = np.abs(np.diff(a_mag) / dt)

    return np.array([
        float(a_mag.max()),
        float(a_mag.mean()),
        float(a_mag.std()),
        float(jerk.max()),
        float(np.abs(df["gx"]).max()),
        float(np.abs(df["gy"]).max()),
        float(np.abs(df["gz"]).max()),
        float((a_mag**2).sum() * dt),
    ], dtype=float)

def _sev_features(df: pd.DataFrame) -> np.ndarray:
    a_mag = np.sqrt(df["ax"]**2 + df["ay"]**2 + df["az"]**2)

    dt = float(np.mean(np.diff(df["t"])))
    if dt <= 0:
        dt = 1e-3

    jerk = np.abs(np.diff(a_mag) / dt)

    return np.array([
        float(a_mag.max()),
        float(jerk.max()),
        float(np.abs(df["gx"]).max()),
        float((a_mag**2).sum() * dt),
    ], dtype=float)

def find_event_dir(extracted_dir: str) -> str:
    """
    Your zip might extract:
    - imu.csv directly inside extracted_dir
    OR
    - extracted_dir/<one_folder>/imu.csv
    This returns the correct folder that contains imu.csv.
    """
    direct = os.path.join(extracted_dir, "imu.csv")
    if os.path.exists(direct):
        return extracted_dir

    # search one nested folder
    items = [os.path.join(extracted_dir, x) for x in os.listdir(extracted_dir)]
    folders = [x for x in items if os.path.isdir(x)]

    if len(folders) == 1:
        nested = os.path.join(folders[0], "imu.csv")
        if os.path.exists(nested):
            return folders[0]

    raise FileNotFoundError("imu.csv not found in extracted zip folder")

def predict_event(event_dir: str) -> dict:
    """
    event_dir must contain imu.csv.
    Returns {"crash":0/1, "severity":"light/heavy"(if crash=1)}
    """
    load_models()

    imu_path = os.path.join(event_dir, "imu.csv")
    if not os.path.exists(imu_path):
        return {"error": "imu.csv not found"}

    df = pd.read_csv(imu_path)

    required = {"t", "ax", "ay", "az", "gx", "gy", "gz"}
    if not required.issubset(df.columns):
        return {"error": f"imu.csv missing columns. Required: {sorted(required)}"}

    crash = int(_crash_model.predict(_crash_features(df).reshape(1, -1))[0])
    result = {"crash": crash}

    if crash == 1:
        heavy = int(_sev_model.predict(_sev_features(df).reshape(1, -1))[0])
        result["severity"] = "heavy" if heavy else "light"

    return result
