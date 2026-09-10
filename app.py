import base64
from groq import Groq
import streamlit as st

# Hide the header anchor link icon
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

# Updated prompt to include legal rules in brackets and ignore dummy/lorem ipsum text
prompt = (
    "Analyze these product images for Legal Metrology compliance based on the 7"
    " mandatory declarations. Ignore placeholder text like 'Lorem ipsum' or"
    " dummy content. For each declaration, include the exact Legal Metrology"
    " rule/section in brackets:\n1. Name (Rule 6 - Common/Generic Name of the"
    " Commodity)\n2. Manufacturer (Rule 6 - Name and complete address of"
    " manufacturer/packer/importer)\n3. Net Quantity (Rule 6 - Net quantity in"
    " terms of standard weight/measure/number)\n4. MRP (Rule 6 - Maximum Retail"
    " Price inclusive of all taxes)\n5. Month/Year of packing (Rule 6 -"
    " Month and year of manufacture/packing/import)\n6. Customer Care (Rule 6"
    " - Consumer care email/phone/address details)\n7. Country of Origin (Rule"
    " 6/Customs - Country of origin of manufacture)"
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

      # Aggressive cleaner to completely strip thinking tags and internal reasoning text
      if "</think>" in raw_output:
        final_output = raw_output.split("</think>")[-1].strip()
      else:
        final_output = raw_output

      # Safety backup check if the whole output was trapped inside think tags
      if not final_output and "<think>" in raw_output:
        final_output = (
            raw_output.replace("<think>", "")
            .replace("</think>", "")
            .strip()
        )

      st.success("Audit Complete!")
      st.markdown("---")
      st.markdown(final_output)

    except Exception as e:
      st.error(f"Groq API Error: {e}")
