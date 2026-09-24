import base64
import json
import os
import subprocess
import sys
import fitz  # PyMuPDF for reliable PDF-to-Image rendering
import streamlit as st

st.set_page_config(
    page_title="Minimalist CV Builder", page_icon="📄", layout="wide"
)

# Initialize session state counters for dynamic fields
if "exp_count" not in st.session_state:
    st.session_state.exp_count = 1

if "edu_count" not in st.session_state:
    st.session_state.edu_count = 1

st.markdown(
    """
    <style>
    .main { background-color: #F8FAFC; }
    h1 { color: #0F172A; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    .stButton > button {
        background-color: #4F46E5;
        color: white;
        border-radius: 6px;
        font-weight: 500;
        border: none;
        padding: 0.5rem 1rem;
        transition: background-color 0.2s;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #4338CA;
        color: white;
    }
    @media (max-width: 768px) {
        .block-container { padding: 1rem 1rem; }
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📄 Clean CV Generator")
st.markdown(
    "<p style='color: #64748B; font-size: 1rem; margin-top: -10px; margin-bottom: 25px;'>Fill out your details below — your live PDF preview updates automatically as you type.</p>",
    unsafe_allow_html=True,
)

# Responsive Layout: Side-by-side on desktop, auto-stacks on mobile/tablets
form_col, preview_col = st.columns([1, 1], gap="large")

with form_col:
    st.subheader("👤 Personal Information")

    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full Name *", value="", placeholder="e.g. John Doe")
        title = st.text_input("Target Title *", value="", placeholder="e.g. Senior Software Engineer")
        email = st.text_input("Email *", value="", placeholder="e.g. john@example.com")
    with c2:
        location = st.text_input("Location", value="", placeholder="e.g. New York, NY")
        linkedin = st.text_input("LinkedIn", value="", placeholder="e.g. linkedin.com/in/johndoe")
        
        # Phone number with responsive country code dropdown & input field
        st.markdown("<p style='font-size: 14px; font-weight: 500; margin-bottom: 6px; margin-top: 10px;'>Phone Number</p>", unsafe_allow_html=True)
        p_col1, p_col2 = st.columns([1.8, 2.2])
        with p_col1:
            phone_code = st.selectbox(
                "Country Code",
                ["+1 US/CA", "+63 PH", "+44 UK", "+61 AU", "+91 IN", "+49 DE", "+81 JP", "+971 AE"],
                label_visibility="collapsed"
            )
        with p_col2:
            phone_number_only = st.text_input(
                "Phone Number Input",
                value="",
                placeholder="912 345 6789",
                label_visibility="collapsed"
            )
        prefix = phone_code.split(" ")[0]
        phone = f"{prefix} {phone_number_only}".strip() if phone_number_only else ""

    contacts_input = st.text_input(
        "Additional Contacts / Links (comma separated)",
        value="",
        placeholder="e.g. github.com/johndoe, portfolio.com"
    )

    summary = st.text_area(
        "Professional Summary",
        height=90,
        value="",
        placeholder="Write a short summary highlighting your key background and career objectives..."
    )

    st.markdown("---")

    # --- Work Experience ---
    st.subheader("💼 Work Experience")
    experience_inputs = []

    for i in range(st.session_state.exp_count):
        st.markdown(f"**Experience Entry {i+1}**")

        ec1, ec2 = st.columns(2)
        with ec1:
            comp = st.text_input(f"Company {i+1}", key=f"comp_{i}", value="", placeholder="e.g. Tech Corp")
            role = st.text_input(f"Role {i+1}", key=f"role_{i}", value="", placeholder="e.g. Software Engineer")
        with ec2:
            dur = st.text_input(f"Duration {i+1}", key=f"dur_{i}", value="", placeholder="e.g. Jan 2021 – Present")

        h_a = st.text_input(f"Highlight 1 (Position {i+1})", key=f"h_a_{i}", value="", placeholder="e.g. Developed core microservices using Python.")
        h_b = st.text_input(f"Highlight 2 (Position {i+1})", key=f"h_b_{i}", value="", placeholder="e.g. Reduced API response times by 30%.")
        st.markdown("")

        experience_inputs.append({
            "company": comp,
            "role": role,
            "duration": dur,
            "highlights": [h for h in [h_a, h_b] if h],
        })

    if st.button("➕ Add Another Experience Field", type="secondary"):
        st.session_state.exp_count += 1
        st.rerun()

    st.markdown("---")

    # --- Education ---
    st.subheader("🎓 Education")
    education_inputs = []

    for i in range(st.session_state.edu_count):
        st.markdown(f"**Education Entry {i+1}**")

        ed1, ed2, ed3 = st.columns(3)
        with ed1:
            edu_deg = st.text_input(f"Degree {i+1}", key=f"edu_deg_{i}", value="", placeholder="e.g. B.S. Computer Science")
        with ed2:
            edu_inst = st.text_input(f"Institution {i+1}", key=f"edu_inst_{i}", value="", placeholder="e.g. University Name")
        with ed3:
            edu_yr = st.text_input(f"Year {i+1}", key=f"edu_yr_{i}", value="", placeholder="e.g. 2017 – 2021")
        st.markdown("")

        education_inputs.append({
            "degree": edu_deg,
            "institution": edu_inst,
            "year": edu_yr,
        })

    if st.button("➕ Add Another Education Field", type="secondary"):
        st.session_state.edu_count += 1
        st.rerun()

    st.markdown("---")

    # --- Skills ---
    st.subheader("🛠️ Core Skills")
    skills_input = st.text_input(
        "Skills (comma separated)",
        value="",
        placeholder="e.g. Python, JavaScript, React, SQL, Git"
    )

# --- Automatic Data Processing & PDF Compilation ---
final_experiences = [job for job in experience_inputs if job["company"].strip()]
final_education = [edu for edu in education_inputs if edu["degree"].strip()]

new_data = {
    "personal_info": {
        "name": name,
        "title": title,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "summary": summary,
    },
    "contacts": [c.strip() for c in contacts_input.split(",") if c.strip()],
    "education": final_education,
    "experience": final_experiences,
    "projects": [],
    "skills": [s.strip() for s in skills_input.split(",") if s.strip()],
}

with open("data.json", "w") as f:
    json.dump(new_data, f, indent=4)

try:
    subprocess.run(
        [sys.executable, "generate_cv.py"],
        check=True,
        capture_output=True,
        text=True,
    )
except subprocess.CalledProcessError as e:
    st.error(f"Error compiling PDF:\n{e.stderr}")

# --- Render Live Preview Column ---
with preview_col:
    st.subheader("👁️ Live PDF Preview")

    if os.path.exists("cv.pdf"):
        with open("cv.pdf", "rb") as pdf_file:
            PDFbyte = pdf_file.read()
            st.download_button(
                label="📥 Download cv.pdf",
                data=PDFbyte,
                file_name="cv.pdf",
                mime="application/pdf",
            )

        # Convert PDF pages to PNG images for robust rendering
        try:
            doc = fitz.open("cv.pdf")
            for page in doc:
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                st.image(img_bytes, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering PDF preview: {e}")
    else:
        st.info("Generating preview...")