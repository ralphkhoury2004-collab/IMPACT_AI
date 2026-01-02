import os, json
import numpy as np
import pandas as pd
import joblib

CRASH_MODEL = "models/crash_detector.joblib"
SEV_MODEL   = "models/severity_model.joblib"

def crash_features(df):
    a_mag = np.sqrt(df.ax**2 + df.ay**2 + df.az**2)
    dt = np.mean(np.diff(df.t))
    jerk = np.abs(np.diff(a_mag) / dt)
    return np.array([
        a_mag.max(), a_mag.mean(), a_mag.std(),
        jerk.max(),
        np.abs(df.gx).max(), np.abs(df.gy).max(), np.abs(df.gz).max(),
        (a_mag**2).sum() * dt
    ], dtype=float)

def sev_features(df):
    a_mag = np.sqrt(df.ax**2 + df.ay**2 + df.az**2)
    dt = np.mean(np.diff(df.t))
    jerk = np.abs(np.diff(a_mag) / dt)
    return np.array([a_mag.max(), jerk.max(), np.abs(df.gx).max(), (a_mag**2).sum()*dt], dtype=float)

def main(event_dir: str):
    imu_path = os.path.join(event_dir, "imu.csv")
    df = pd.read_csv(imu_path)

    crash_clf = joblib.load(CRASH_MODEL)
    sev_clf = joblib.load(SEV_MODEL)

    crash = int(crash_clf.predict(crash_features(df).reshape(1,-1))[0])
    result = {"crash": crash}

    if crash == 1:
        heavy = int(sev_clf.predict(sev_features(df).reshape(1,-1))[0])
        result["severity"] = "heavy" if heavy else "light"

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
