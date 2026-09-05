import os
import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(
    page_title="MetroScan-AI", page_icon="🚇", layout="centered"
)

st.title("MetroScan-AI 🚇")
st.write("AI-powered analysis tool initialized and ready.")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
  st.error(
      "API Key not found! Please add your GEMINI_API_KEY under Streamlit"
      " Cloud -> App Settings -> Secrets."
  )
else:
  genai.configure(api_key=api_key)
  model = genai.GenerativeModel("gemini-2.5-flash")

  uploaded_file = st.file_uploader(
      "Upload or capture an image for scanning...",
      type=["jpg", "jpeg", "png"],
  )

  if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Scan", use_column_width=True)

    if st.button("Run Analysis"):
      with st.spinner("Analyzing with Gemini..."):
        try:
          response = model.generate_content([
              image,
              "Analyze this image for MetroScan-AI and provide details.",
          ])
          st.success("Analysis Complete!")
          st.write(response.text)
        except Exception as e:
          st.error(f"An error occurred during analysis: {e}")
