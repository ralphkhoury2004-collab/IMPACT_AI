import streamlit as st
import requests
import urllib.parse

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="IMPACT Dashboard", layout="wide")
st.title("IMPACT Claims Dashboard")

# 1) Backend check
try:
    r = requests.get(f"{API}/health", timeout=3)
    st.success(f"Backend OK ✅  {r.json()}")
except Exception:
    st.error("Backend not reachable ❌  Start FastAPI first on http://127.0.0.1:8000")
    st.stop()

# Optional: refresh button
if st.button("🔄 Refresh claims"):
    st.rerun()

# 2) Load claims
claims = requests.get(f"{API}/claims", timeout=3).json().get("claims", [])
if not claims:
    st.warning("No claims yet. Upload an event ZIP in http://127.0.0.1:8000/docs → POST /upload_event")
    st.stop()

claim_id = st.selectbox("Select a claim", claims)

# 3) Load claim details
data = requests.get(f"{API}/claims/{claim_id}", timeout=3).json()

st.subheader("AI Result")
st.json(data)

crash = data.get("crash", None)
severity = data.get("severity", "-")

c1, c2 = st.columns(2)
c1.metric("Crash", "YES" if crash == 1 else "NO")
c2.metric("Severity", severity)

# 4) Emergency WhatsApp (manual send via click-to-chat)
if data.get("emergency_required"):
    st.error("🚨 EMERGENCY REQUIRED (Heavy crash detected)")

    msg = data.get("emergency_message", "").strip()

    # Support BOTH formats:
    # - single number: data["emergency_to"] = "+961..."
    # - list: data["emergency_contacts"] = ["+961..", "+961.."]
    recipients = []

    one_to = data.get("emergency_to", "").strip()
    if one_to:
        recipients = [one_to]
    else:
        recipients = data.get("emergency_contacts", []) or []

    if not msg:
        st.warning("Emergency message is missing from backend result.")
    else:
        st.write("WhatsApp message:")
        st.code(msg)

    if not recipients:
        st.warning("No emergency recipient number found. Set it in backend/.env and return it from the backend.")
    else:
        st.write("Open WhatsApp chat (message will be pre-filled):")
        for num in recipients:
            digits = str(num).replace("+", "").replace(" ", "")
            link = f"https://wa.me/{digits}?text={urllib.parse.quote(msg)}"
            st.markdown(f"- **{num}** → [Open WhatsApp chat]({link})")
else:
    st.info("No emergency required for this claim.")
