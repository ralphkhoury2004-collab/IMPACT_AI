import os, json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

DATA_DIR = "data/events"
MODEL_OUT = "models/severity_model.joblib"

def features_from_csv(path: str) -> np.ndarray:
    df = pd.read_csv(path)
    a_mag = np.sqrt(df.ax**2 + df.ay**2 + df.az**2)
    dt = np.mean(np.diff(df.t))
    jerk = np.abs(np.diff(a_mag) / dt)
    return np.array([
        a_mag.max(),
        jerk.max(),
        np.abs(df.gx).max(),
        (a_mag**2).sum() * dt,
    ], dtype=float)

def main():
    X, y = [], []
    for ev in sorted(os.listdir(DATA_DIR)):
        ev_path = os.path.join(DATA_DIR, ev)
        imu_path = os.path.join(ev_path, "imu.csv")
        label_path = os.path.join(ev_path, "label.json")

        with open(label_path, "r") as f:
            lab = json.load(f)

        if int(lab["crash"]) != 1:
            continue
        if lab["severity"] not in ("light", "heavy"):
            continue

        X.append(features_from_csv(imu_path))
        y.append(1 if lab["severity"] == "heavy" else 0)

    X = np.vstack(X)
    y = np.array(y)

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    clf = RandomForestClassifier(n_estimators=300, random_state=42)
    clf.fit(Xtr, ytr)

    pred = clf.predict(Xte)
    print(classification_report(yte, pred))

    os.makedirs("models", exist_ok=True)
    joblib.dump(clf, MODEL_OUT)
    print("Saved:", MODEL_OUT)

if __name__ == "__main__":
    main()
