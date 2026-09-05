import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="Metro-Scan AI", page_icon="📦", layout="centered")

st.title("📦 Metro-Scan AI: Label Compliance Scanner")
st.write("Upload a product label file or click the camera button below to snap a live photo.")

# Hardcoded API key for seamless consumer experience
GEMINI_API_KEY = "YOUR_API_KEY_HERE"

# Initialize session state so the camera starts closed
if "show_camera" not in st.session_state:
    st.session_state.show_camera = False

image = None

# Option 1: File Uploader
uploaded_file = st.file_uploader("📁 Upload Product Label Image", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.session_state.show_camera = False
    except Exception:
        st.error("⚠️ Could not read this image file. Please try a different standard JPG or PNG image.")

st.markdown("---")

# Option 2: Dedicated Camera Button
st.markdown("### 📸 Live Camera Capture")

if not st.session_state.show_camera:
    if st.button("📷 Camera"):
        st.session_state.show_camera = True
        st.rerun()
else:
    if st.button("❌ Close Camera"):
        st.session_state.show_camera = False
        st.rerun()
        
    st.markdown("⚠️ **Rule:** Photo has to be clear, well-lit, and all label text must be fully legible for accurate compliance auditing.")
    camera_file = st.camera_input("Take a picture of the product label")
    if camera_file is not None:
        try:
            image = Image.open(camera_file)
        except Exception:
            st.error("⚠️ Could not read camera input.")

# Display the preview at the bottom before scanning
if image is not None:
    st.markdown("---")
    st.image(image, caption="Selected Product Label Preview", use_container_width=True)

st.markdown("---")

if st.button("Scan Label", type="primary"):
    if image is None:
        st.warning("⚠️ Please upload a valid image file or capture a live photo first.")
    else:
        with st.spinner("Analyzing label for compliance..."):
            try:
                client = genai.Client(api_key=GEMINI_API_KEY)
                
                prompt = """
                You are a Senior Legal Metrology Inspector in India.
                First, check the quality of this image. If the image is blurry, dark, unreadable, or if the text on the product label is not visible properly, do NOT perform an audit and output ONLY this exact sentence: 
                "The photo is not visible properly, upload a new photo."
                
                If the image is clear and text is legible, examine the product package image carefully. Read all text visible on the label (OCR) and check if the following 7 mandatory declarations are present:
                
                1. MRP (Maximum Retail Price - inclusive of all taxes)
                2. Date of Manufacture / Packing / Import month and year
                3. Net Quantity / Weight
                4. Manufacturer / Packer / Importer Complete Name & Address
                5. Generic Name of the product
                6. Consumer Care / Customer Support Contact Details
                7. Batch Number / Lot Number
                
                Provide a detailed Red/Green compliance dashboard. 
                - Use 🟢 PASS if a field is clearly legible and present.
                - Use 🔴 FAIL if a field is missing or unreadable.
                - Briefly note what is found or missing for each.
                Keep the report structured, professional, and clean for a hackathon presentation.
                """
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=[prompt, image]
                )
                
                st.markdown("### 📊 Compliance Audit Report")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")