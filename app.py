import base64
from groq import Groq
import streamlit as st

# Initialize the Groq client using Streamlit secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("Metro-Scan AI (Powered by Groq)")

# 1. Allow multiple image uploads
uploaded_images = st.file_uploader(
    "Upload product label photos (Front, Back, MRP panel, etc.)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

prompt = st.text_area(
    "Analysis Prompt",
    "Check these product images against Legal Metrology packaging rules (7"
    " mandatory declarations).",
)

if uploaded_images and st.button("Run Compliance Audit"):
  with st.spinner(
      "Analyzing multiple angles with ultra-fast Groq inference..."
  ):
    # Build the message payload array
    content_payload = [{"type": "text", "text": prompt}]

    # Loop through each uploaded image, encode to base64, and add to payload
    for img in uploaded_images:
      bytes_data = img.getvalue()
      base64_image = base64.b64encode(bytes_data).decode("utf-8")
      content_payload.append({
          "type": "image_url",
          "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
      })

    try:
      # Call Groq's high-speed vision model
      completion = client.chat.completions.create(
          model="qwen/qwen3.6-27b",  # Groq's robust vision model
          messages=[{"role": "user", "content": content_payload}],
          temperature=0.1,
      )

      st.success("Audit Complete!")
      st.markdown("---")
      st.markdown(completion.choices[0].message.content)

    except Exception as e:
      st.error(f"Groq API Error: {e}")
