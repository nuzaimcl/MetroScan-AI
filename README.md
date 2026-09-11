Metro-Scan AI: Technical Algorithm & Architecture Specification
1. System Overview
Metro-Scan AI is an advanced computer vision compliance auditing system designed to verify multi-angle product packaging against Rule 6 of the Indian Legal Metrology (Packaged Commodities) Rules, 2011. The system ingests multi-image inputs representing different sides of a single product package, structures them into a unified multimodal payload, queries a high-performance Vision-Language Model (VLM) via Groq, strips internal reasoning tokens, and produces a structured audit report detailing explicit [PASS] or [FAIL] compliance statuses alongside required corrective actions.

2. Input Acquisition & State Management
Mode Selection: The application uses Streamlit session state (st.session_state.input_mode) to toggle between two distinct input mechanisms:

Bulk File Uploader: st.file_uploader accepting standard image formats (JPG, JPEG, PNG) with multi-file support.

Live Camera Capture: Progressive live snapshots captured via st.camera_input, appending unique frames sequentially to st.session_state.live_photos while filtering out duplicate consecutive captures.

Pipeline Normalization: Active images from either input mode are consolidated into a unified uploaded_images array.

3. Multimodal Preprocessing & Payload Construction
For every image present in the active session array, the preprocessing pipeline executes the following sequence:

Byte Extraction: Read the raw byte buffer from the uploaded file object (img.getvalue()).

Base64 Encoding: Convert the raw binary stream into a UTF-8 decoded Base64 string (base64.b64encode).

Payload Structuring: Format the request payload for the Groq API client:

Text Component: Contains strict audit instructions and evaluation criteria emphasizing multi-image aggregation (treating all uploaded images as different sides of the exact same package).

Image Components: Array of multimodal image objects embedding Base64 data URLs (data:image/jpeg;base64,...).

4. Inference & VLM Execution Algorithm
Model Dispatch: Sends the constructed multimodal payload to the qwen/qwen3.6-27b model via the Groq SDK.

Hyperparameter Configuration:

temperature = 0.1: Minimized to enforce deterministic, analytical consistency and eliminate generative hallucinations.

max_tokens = 800: Configured to operate within Groq's free-tier output tokens per minute (OTPM) rate limits.

Prompt Engineering Constraints:

Enforces cross-image context (combining attributes found across any uploaded side).

Enforces strict validation rules (e.g., rejecting vegetarian green dots as Country of Origin, requiring explicit "MRP" labeling, and treating "Lorem ipsum" placeholders as failures).

5. Output Sanitization & Parsing Algorithm
To remove internal model chain-of-thought tokens (<think> blocks) and ensure a clean user interface:

Regex Substitution: Scan the raw model response string (raw_output) and strip all text encapsulated inside reasoning tags using regular expression pattern matching (re.sub(r'<think>.*?</think>', '', raw_output, flags=re.DOTALL)).

Fallback Isolation: In edge cases where token limits result in unclosed tags, execute a secondary safety check to isolate valid output text.

Dynamic Rendering: Display the sanitized audit report using markdown formatting within the Streamlit application interface.
