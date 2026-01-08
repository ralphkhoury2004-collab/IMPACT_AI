import streamlit as st
import requests
import urllib.parse
API = "http://127.0.0.1:8000"

st.set_page_config(page_title="IMPACT Dashboard", layout="wide")
st.title("IMPACT Claims Dashboard")

# 1) Backend check
try:
    r = requests.get(f"{API}/health", timeout=2)
    st.success(f"Backend OK ✅  {r.json()}")
except Exception as e:
    st.error("Backend not reachable ❌  Start FastAPI first on http://127.0.0.1:8000")
    st.stop()

# 2) Load claims
claims = requests.get(f"{API}/claims", timeout=2).json().get("claims", [])
if not claims:
    st.warning("No claims yet. Upload an event ZIP in http://127.0.0.1:8000/docs → POST /upload_event")
    st.stop()

claim_id = st.selectbox("Select a claim", claims)

# 3) Load claim details
data = requests.get(f"{API}/claims/{claim_id}", timeout=2).json()

st.subheader("AI Result")
st.json(data)

crash = data.get("crash", None)
severity = data.get("severity", "-")

c1, c2 = st.columns(2)
c1.metric("Crash", "YES" if crash == 1 else "NO")
c2.metric("Severity", severity)
import urllib.parse

if data.get("emergency_required"):
    st.error("🚨 EMERGENCY REQUIRED (Heavy crash detected)")

    msg = data.get("emergency_message", "")
    contacts = data.get("emergency_contacts", [])

    st.write("Copy the message below and send it to both WhatsApp numbers:")
    st.code(msg)

    for num in contacts:
        # WhatsApp click-to-chat link
        # works with digits only
        digits = num.replace("+", "").replace(" ", "")
        link = f"https://wa.me/{digits}?text={urllib.parse.quote(msg)}"
        st.markdown(f"- Send to **{num}**: {link}")
