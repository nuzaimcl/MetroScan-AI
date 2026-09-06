import asyncio
import os
import sys

if sys.platform == "win32":
  asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from PIL import Image
from google import genai
import streamlit as st

st.set_page_config(
    page_title="MetroScan-AI Auditor", page_icon="🔍", layout="centered"
)

# Load API Key securely from Streamlit Cloud Secrets
api_key = None
try:
  api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
  api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
  st.error("GEMINI_API_KEY not configured in deployment secrets.")
  st.stop()

client = genai.Client(api_key=api_key)

st.title("🔍 MetroScan-AI Scanner")
st.markdown("Upload packaging scans for instant Legal Metrology compliance checks.")

uploaded_file = st.file_uploader(
    "Choose Packaging Image (JPG, PNG)", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  try:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Scan", use_container_width=True)

    if st.button("Run Compliance Analysis", type="primary"):
      with st.spinner("Analyzing Legal Metrology compliance declarations..."):
        prompt = (
            "Analyze this packaging image strictly based on Legal Metrology "
            "(Packaged Commodities) Rules. Evaluate the following 7 mandatory declarations:\n"
            "1. Name and address of the manufacturer/packer/importer\n"
            "2. Common or generic name of the commodity\n"
            "3. Net quantity\n"
            "4. Month and year of packing/manufacturing/import\n"
            "5. Retail Sale Price (MRP inclusive of all taxes)\n"
            "6. Consumer care/grievance details\n"
            "7. Country of origin (if imported) or statutory safety/declaration standards\n\n"
            "Structure your output strictly using these sections:\n"
            "- **Compliance Score**: [X] out of 7 items are approved.\n"
            "- **Approved Elements**: List compliant declarations found.\n"
            "- **Non-Approved Elements**: List missing or defective elements, and for every "
            "non-approved item, you MUST include the specific Legal Metrology rule/section violation in brackets (e.g., [Rule 6(1) of LM PC Rules]).\n"
            "- **Final Product Verdict**: State clearly whether the product is 'APPROVED' or 'NOT APPROVED' for market distribution."
        )

        response = client.models.generate_content(
            model="gemini-3.7-flash", contents=[image, prompt]
        )

        st.success("Inspection Complete!")
        st.markdown("---")
        st.markdown(response.text)

  except Exception as e:
    st.error(f"An error occurred during analysis: {e}")
else:
  st.info("Upload an image above to start the automated audit.")
