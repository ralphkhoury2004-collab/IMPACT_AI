from fastapi import FastAPI, UploadFile, File, HTTPException
import os, uuid, shutil, zipfile, json
from .ai_infer import predict_event
from .config import EMERGENCY_NUMBERS

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
STORE_DIR = os.path.join(BASE_DIR, "storage")
EVENTS_DIR = os.path.join(STORE_DIR, "events")
RESULTS_DIR = os.path.join(STORE_DIR, "results")

os.makedirs(EVENTS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


def safe_extract_zip(zip_path: str, extract_to: str):
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.infolist():
            # prevent zip slip
            member_path = os.path.normpath(os.path.join(extract_to, member.filename))
            if not member_path.startswith(os.path.abspath(extract_to)):
                raise HTTPException(status_code=400, detail="Unsafe zip content")
        z.extractall(extract_to)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/upload_event")
async def upload_event(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Upload a .zip event folder")

    claim_id = str(uuid.uuid4())
    claim_dir = os.path.join(EVENTS_DIR, claim_id)
    os.makedirs(claim_dir, exist_ok=True)

    zip_path = os.path.join(claim_dir, file.filename)
    with open(zip_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # unzip into claim_dir/extracted/
    extracted_dir = os.path.join(claim_dir, "extracted")
    os.makedirs(extracted_dir, exist_ok=True)
    safe_extract_zip(zip_path, extracted_dir)

    # zip may contain imu.csv at root or inside a single folder
    event_dir = extracted_dir
    if not os.path.exists(os.path.join(event_dir, "imu.csv")):
        items = [os.path.join(extracted_dir, x) for x in os.listdir(extracted_dir)]
        folders = [x for x in items if os.path.isdir(x)]
        if len(folders) == 1 and os.path.exists(os.path.join(folders[0], "imu.csv")):
            event_dir = folders[0]
        else:
            raise HTTPException(status_code=400, detail="imu.csv not found inside zip")

    # ---- AI inference ----
    result = predict_event(event_dir)

    # ---- Add emergency fields (AFTER predict, BEFORE saving) ----
    # Make sure ai_infer.py sets result["emergency_required"] for heavy crashes.
    if result.get("emergency_required"):
        msg = (
            "IMPACT ALERT: Heavy crash detected.\n"
            f"Claim ID: {claim_id}\n"
            "Please check the driver immediately."
        )
        result["emergency_contacts"] = EMERGENCY_NUMBERS
        result["emergency_message"] = msg
    else:
        result["emergency_contacts"] = []
        result["emergency_message"] = ""

    # ---- Save result ----
    result_path = os.path.join(RESULTS_DIR, f"{claim_id}.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    return {"claim_id": claim_id, "result": result}


@app.get("/claims")
def list_claims():
    ids = []
    for name in os.listdir(RESULTS_DIR):
        if name.endswith(".json"):
            ids.append(name.replace(".json", ""))
    ids.sort()
    return {"claims": ids}


@app.get("/claims/{claim_id}")
def get_claim(claim_id: str):
    path = os.path.join(RESULTS_DIR, f"{claim_id}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Claim not found")
    with open(path, "r") as f:
        return json.load(f)
