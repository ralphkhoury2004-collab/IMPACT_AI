import os
import sys
import json
import pandas as pd

REQUIRED = ["meta.json", "label.json", "imu.csv", "obd.csv", "gps.csv", "video.mp4"]
IMU_COLS = ["t","ax","ay","az","gx","gy","gz"]

def main(event_dir):
    # 1) required files
    missing = [f for f in REQUIRED if not os.path.exists(os.path.join(event_dir, f))]
    if missing:
        print("❌ Missing files:", missing)
        sys.exit(1)
    print("✅ All required files exist")

    # 2) meta.json parse
    with open(os.path.join(event_dir, "meta.json"), "r") as f:
        meta = json.load(f)
    for k in ["event_id","device_id","session_id","sampling_hz","duration_s"]:
        if k not in meta:
            print(f"❌ meta.json missing key: {k}")
            sys.exit(1)
    print("✅ meta.json keys OK")

    # 3) imu.csv columns
    imu = pd.read_csv(os.path.join(event_dir, "imu.csv"))
    for c in IMU_COLS:
        if c not in imu.columns:
            print("❌ imu.csv missing column:", c)
            print("Found columns:", list(imu.columns))
            sys.exit(1)
    if imu.shape[0] < 10:
        print("❌ imu.csv too few rows:", imu.shape[0])
        sys.exit(1)
    print("✅ imu.csv format OK")

    # 4) obd.csv / gps.csv exist + basic parse
    pd.read_csv(os.path.join(event_dir, "obd.csv"))
    pd.read_csv(os.path.join(event_dir, "gps.csv"))
    print("✅ obd.csv and gps.csv readable")

    # 5) video exists and non-empty
    size = os.path.getsize(os.path.join(event_dir, "video.mp4"))
    if size < 1000:
        print("❌ video.mp4 looks too small (maybe not a real mp4):", size, "bytes")
        sys.exit(1)
    print("✅ video.mp4 looks valid (size:", size, "bytes)")

    print("\n🎉 Event folder PASSED validation:", event_dir)

if __name__ == "__main__":
    main(sys.argv[1])
