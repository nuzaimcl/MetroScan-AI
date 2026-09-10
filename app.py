import base64
from groq import Groq
import streamlit as st

st.markdown(
    """
    <style>
    [data-testid="stHeaderActionElements"] {
        display: none;
    }
    </style>
""",
    unsafe_allow_html=True,
)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("Metro-Scan AI | Compliance Auditor")

st.markdown("<br>", unsafe_allow_html=True)

if "input_mode" not in st.session_state:
  st.session_state.input_mode = "Upload Images"

col1, col2 = st.columns(2)
with col1:
  if st.button("📁 Upload Images", use_container_width=True):
    st.session_state.input_mode = "Upload Images"
with col2:
  if st.button("📸 Take Live Photos", use_container_width=True):
    st.session_state.input_mode = "Take Live Photos"

uploaded_images = []

if st.session_state.input_mode == "Upload Images":
  files = st.file_uploader(
      "Upload product label photos",
      type=["jpg", "jpeg", "png"],
      accept_multiple_files=True,
  )
  if files:
    uploaded_images.extend(files)
else:
  if "live_photos" not in st.session_state:
    st.session_state.live_photos = []

  camera_file = st.camera_input("Take a photo of the product label")

  if camera_file is not None:
    if (
        not st.session_state.live_photos
        or st.session_state.live_photos[-1].getvalue()
        != camera_file.getvalue()
    ):
      st.session_state.live_photos.append(camera_file)
      st.rerun()

  if st.session_state.live_photos:
    st.write(f"Captured Live Photos: {len(st.session_state.live_photos)}")
    if st.button("Clear Live Photos"):
      st.session_state.live_photos = []
      st.rerun()
    uploaded_images.extend(st.session_state.live_photos)

if uploaded_images:
  st.subheader("Image Preview")
  cols = st.columns(min(len(uploaded_images), 4))
  for idx, img in enumerate(uploaded_images):
    with cols[idx % len(cols)]:
      st.image(img, use_container_width=True)

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
