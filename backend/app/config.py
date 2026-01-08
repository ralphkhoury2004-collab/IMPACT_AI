from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
load_dotenv(BASE_DIR / ".env")  # always load backend/.env

EMERGENCY_NUMBERS = [
    x.strip() for x in os.getenv("EMERGENCY_NUMBERS", "").split(",") if x.strip()
]
