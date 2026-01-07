import sys, zipfile
import numpy as np
import pandas as pd

ACC_FILE = "Accelerometer.csv"
GYRO_FILE = "Gyroscope.csv"

def clean(df, time_col="Time (s)"):
    df = df.copy()
    df = df.sort_values(time_col)
    df = df.drop_duplicates(time_col)
    df = df.reset_index(drop=True)
    return df

def interp_fill(t_src, y_src, t_tgt):
    # fills out-of-range with nearest endpoint value
    return np.interp(t_tgt, t_src, y_src, left=y_src[0], right=y_src[-1])

def main(zip_path, out_csv):
    with zipfile.ZipFile(zip_path, "r") as z:
        if ACC_FILE not in z.namelist() or GYRO_FILE not in z.namelist():
            raise SystemExit(f"ZIP must contain {ACC_FILE} and {GYRO_FILE}. Found: {z.namelist()}")

        with z.open(ACC_FILE) as f:
            acc = pd.read_csv(f)
        with z.open(GYRO_FILE) as f:
            gyro = pd.read_csv(f)

    acc = clean(acc)
    gyro = clean(gyro)

    # Use accelerometer timeline as the main timeline
    t_acc = acc["Time (s)"].to_numpy()
    t0 = float(t_acc[0])
    t = t_acc - t0

    ax = acc["Acceleration x (m/s^2)"].to_numpy()
    ay = acc["Acceleration y (m/s^2)"].to_numpy()
    az = acc["Acceleration z (m/s^2)"].to_numpy()

    # Interpolate gyro onto accel timeline
    t_g = gyro["Time (s)"].to_numpy() - t0
    gx = interp_fill(t_g, gyro["Gyroscope x (rad/s)"].to_numpy(), t)
    gy = interp_fill(t_g, gyro["Gyroscope y (rad/s)"].to_numpy(), t)
    gz = interp_fill(t_g, gyro["Gyroscope z (rad/s)"].to_numpy(), t)

    out = pd.DataFrame({"t": t, "ax": ax, "ay": ay, "az": az, "gx": gx, "gy": gy, "gz": gz})
    out.to_csv(out_csv, index=False)
    print("Saved:", out_csv)
    print("Rows:", len(out), "Duration(s):", round(float(out["t"].iloc[-1]), 3))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python phyphox_zip_to_imu.py input.zip output_imu.csv")
    main(sys.argv[1], sys.argv[2])
