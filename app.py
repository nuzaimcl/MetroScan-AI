import base64
from groq import Groq
import streamlit as st

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("Metro-Scan AI (Groq Powered)")

upload_option = st.radio(
    "Choose Input Method", ("Upload Images", "Take Live Photo")
)

uploaded_images = []

if upload_option == "Upload Images":
  files = st.file_uploader(
      "Upload product label photos",
      type=["jpg", "jpeg", "png"],
      accept_multiple_files=True,
  )
  if files:
    uploaded_images.extend(files)
else:
  camera_file = st.camera_input("Take a photo of the product label")
  if camera_file:
    uploaded_images.append(camera_file)

prompt = (
    "Check these product images against Legal Metrology packaging rules (7"
    " mandatory declarations: Name, Manufacturer, Net Quantity, MRP, Month/Year"
    " of packing, Customer Care, and Country of Origin)."
)

if uploaded_images and st.button("Run Compliance Audit"):
  with st.spinner("Analyzing with Groq..."):
    content_payload = [{"type": "text", "text": prompt}]

    for img in uploaded_images:
      bytes_data = img.getvalue()
      base64_image = base64.b64encode(bytes_data).decode("utf-8")
      content_payload.append({
          "type": "image_url",
          "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
      })

    try:
      completion = client.chat.completions.create(
          model="qwen/qwen3.6-27b",
          messages=[{"role": "user", "content": content_payload}],
          temperature=0.1,
          max_tokens=800,
      )

      raw_output = completion.choices[0].message.content
      if "</think>" in raw_output:
        final_output = raw_output.split("</think>")[-1].strip()
      else:
        final_output = raw_output

      st.success("Audit Complete!")
      st.markdown("---")
      st.markdown(final_output)

    except Exception as e:
      st.error(f"Groq API Error: {e}")
