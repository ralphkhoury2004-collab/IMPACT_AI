import os, json
import numpy as np
import pandas as pd

def make_event(out_dir: str, crash: int, severity: str):
    os.makedirs(out_dir, exist_ok=True)
    fs = 200  # Hz
    T = 5     # seconds
    t = np.arange(0, T, 1/fs)

    # base noise
    ax = 0.2*np.random.randn(len(t))
    ay = 0.2*np.random.randn(len(t))
    az = 9.81 + 0.2*np.random.randn(len(t))
    gx = 0.5*np.random.randn(len(t))
    gy = 0.5*np.random.randn(len(t))
    gz = 0.5*np.random.randn(len(t))

    # inject crash spike
    if crash == 1:
        idx = int(2.5*fs)
        amp = 6 if severity == "light" else 18
        ax[idx:idx+10] += amp*np.hanning(10)
        gx[idx:idx+20] += (amp/3)*np.hanning(20)

    df = pd.DataFrame({"t": t, "ax": ax, "ay": ay, "az": az, "gx": gx, "gy": gy, "gz": gz})
    df.to_csv(os.path.join(out_dir, "imu.csv"), index=False)

    with open(os.path.join(out_dir, "meta.json"), "w") as f:
        json.dump({"sampling_hz": fs, "duration_s": T}, f, indent=2)

    with open(os.path.join(out_dir, "label.json"), "w") as f:
        json.dump({"crash": crash, "severity": severity}, f, indent=2)

def main():
    base = "data/events"
    os.makedirs(base, exist_ok=True)

    n_no = 60
    n_light = 40
    n_heavy = 40

    k = 0
    for _ in range(n_no):
        make_event(f"{base}/event_{k:04d}", 0, "none"); k += 1
    for _ in range(n_light):
        make_event(f"{base}/event_{k:04d}", 1, "light"); k += 1
    for _ in range(n_heavy):
        make_event(f"{base}/event_{k:04d}", 1, "heavy"); k += 1

    print("Done: generated events in ai/data/events")

if __name__ == "__main__":
    main()
