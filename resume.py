import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import json
# Configure Streamlit Page

st.set_page_config(page_title="AI Resume Parser", page_icon="📄", layout="centered")
st.markdown("""
<style>

/* 1. Hide the top white header gap completely */
[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0) !important;
    background: transparent !important;
}

/* 2. Main background with 4 equal 25% pastel splits (Pink, Beige, Green, Yellow) */
.stApp {
    background: linear-gradient(
        135deg, 
        #ffc5cb 0%, 
        #ffc5cb 25%, 
        #f5ebe0 25%, 
        #f5ebe0 50%, 
        #c3e2b4 50%, 
        #c3e2b4 75%, 
        #fef08a 75%, 
        #fef08a 100%
    );
    background-attachment: fixed;
}

/* Sidebar glass effect */
section[data-testid="stSidebar"] {
    background: rgba(0, 0, 0, 0.04) !important;
    backdrop-filter: blur(25px);
    border-right: 1px solid rgba(0, 0, 0, 0.05);
}

/* Dark text for great readability on light pastels */
h1, h2, h3, p, label, div {
    color: #2d262d !important;
}

/* Clean frosted glass cards */
[data-testid="stFileUploader"],
[data-testid="stExpander"],
.stSuccess,
.stInfo,
.stError {
    background: rgba(255, 255, 255, 0.35) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    backdrop-filter: blur(20px);
    border-radius: 24px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.02);
}

/* 3. FIX: Perfect rounded edges for the Input / API key box wrapper and all child elements */
div[data-baseweb="input"] {
    background: rgba(255, 255, 255, 0.6) !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 30px !important; /* Unified pill shape */
    overflow: hidden !important;    /* Clips any inner leaking edge colors */
}

/* Force inner input containers to inherit the pill shape and fill completely */
div[data-baseweb="input"] > div, 
input {
    border-radius: 30px !important;
    color: #2d262d !important;
}

/* Sleek primary action buttons */
.stButton>button,
.stDownloadButton>button {
    background: rgba(255, 255, 255, 0.6);
    color: #2d262d;
    border-radius: 20px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    height: 55px;
    font-size: 17px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton>button:hover,
.stDownloadButton>button:hover {
    background: #fff;
    border: 1px solid rgba(0, 0, 0, 0.15);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* Header typography styling */
h1 {
    text-align: center;
    font-size: 55px !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
    margin-bottom: 10px;
}

h3 {
    text-align: center;
    color: #4a404a !important;
    font-weight: 400 !important;
    font-size: 20px !important;
    opacity: 0.9;
}

</style>
""", unsafe_allow_html=True)


st.title("AI Resume Parser")
st.markdown(
    "<h3 style='text-align:center;'>Extract and organize candidate information seamlessly</h3>",
    unsafe_allow_html=True
)



# 1. API Key Input Sidebar

st.sidebar.header("Configuration")

api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")



# 2. File Uploader

uploaded_file = st.file_uploader("Upload Candidate Resume (PDF format)", type=["pdf"])



# Helper function to extract text from PDF

def extract_pdf_text(uploaded_file):

    reader = pdf.PdfReader(uploaded_file)

    text = ""

    for page in range(len(reader.pages)):

        text += str(reader.pages[page].extract_text())

    return text



# Core LLM prompt for structured extraction

PROMPT_TEMPLATE = """

You are an expert HR AI assistant. Your task is to analyze the following resume text and extract the information into a structured JSON format. 



Strictly return ONLY valid JSON. Do not include markdown code blocks like ```json ... 

```. Do not include any introductory or concluding text.



If a field is missing, use null or an empty array.



Expected JSON Structure:

{{

    "personal_information": {{

        "full_name": "Extract full name",

        "email": "Extract email address",

        "phone": "Extract phone number",

        "linkedin": "Extract LinkedIn URL if present",

        "location": "City, Country or State"

    }},

    "summary": "Brief professional summary or objective",

    "skills": ["Skill 1", "Skill 2"],

    "work_experience": [

        {{

            "job_title": "Title",

            "company": "Company Name",

            "dates": "Start Date - End Date",

            "responsibilities": ["Responsibility 1", "Responsibility 2"]

        }}

    ],

    "education": [

        {{

            "degree": "Degree/Major",

            "institution": "University/School",

            "graduation_year": "Year"

        }}

    ],

    "certifications_or_projects": ["Item 1", "Item 2"]

}}



Resume Text to Parse:

{resume_text}

"""



if uploaded_file is not None:

    if not api_key:

        st.warning("Please enter your Gemini API Key in the sidebar to proceed.")

    else:

        with st.spinner("Extracting text from PDF..."):

            try:

                # Extract plain text

                resume_text = extract_pdf_text(uploaded_file)

                

                # Configure Gemini

                genai.configure(api_key=api_key)

                model = genai.GenerativeModel('gemini-2.5-flash')

                

                st.success("Text extracted successfully! Sending to AI...")

                

                # Call Gemini API

                formatted_prompt = PROMPT_TEMPLATE.format(resume_text=resume_text)

                response = model.generate_content(formatted_prompt)

                

                # Parse the output

                cleaned_response = response.text.strip()

                

                # Strip out potential markdown code blocks if the LLM adds them by accident

                if cleaned_response.startswith("```"):

                    cleaned_response = cleaned_response.split("```")[1]

                    if cleaned_response.startswith("json"):

                        cleaned_response = cleaned_response[4:]

                

                parsed_json = json.loads(cleaned_response)

                

                st.balloons()

                

                # --- UI Presentation of Extracted Data ---

                st.header("📋 Extracted Information")

                

                # Personal Info Section

                pi = parsed_json.get("personal_information", {})

                st.subheader(f"👤 {pi.get('full_name', 'Name Not Found')}")

                

                col1, col2 = st.columns(2)

                with col1:

                    st.write(f"**✉️ Email:** {pi.get('email', 'N/A')}")

                    st.write(f"**📞 Phone:** {pi.get('phone', 'N/A')}")

                with col2:

                    st.write(f"**📍 Location:** {pi.get('location', 'N/A')}")

                    st.write(f"**🔗 LinkedIn:** {pi.get('linkedin', 'N/A')}")

                

                st.markdown("---")

                

                # Summary

                st.write("**Professional Summary:**")

                st.write(parsed_json.get("summary", "N/A"))

                

                st.markdown("---")

                

                # Skills

                st.write("**🛠️ Key Skills:**")

                skills = parsed_json.get("skills", [])

                if skills:

                    st.write(", ".join(skills))

                else:

                    st.write("No skills found.")

                    

                st.markdown("---")

                

                # Work Experience

                st.write("**💼 Work Experience:**")

                for job in parsed_json.get("work_experience", []):

                    st.markdown(f"**{job.get('job_title')}** at *{job.get('company')}* ({job.get('dates')})")

                    for resp in job.get("responsibilities", []):

                        st.write(f"- {resp}")

                    st.write("")

                    

                st.markdown("---")

                

                # Education

                st.write("**🎓 Education:**")

                for edu in parsed_json.get("education", []):

                    st.write(f"- **{edu.get('degree')}** — {edu.get('institution')} ({edu.get('graduation_year')})")

                

                st.markdown("---")

                

                # Raw JSON Download

                st.subheader("💾 Export Structured Data")

                st.download_button(

                    label="Download Data as JSON File",

                    data=json.dumps(parsed_json, indent=4),

                    file_name=f"{pi.get('full_name', 'parsed_resume')}.json",

                    mime="application/json"

                )

                

                with st.expander("View Raw JSON Output"):

                    st.json(parsed_json)

                    

            except Exception as e:

                st.error(f"An error occurred: {e}")

                st.info("Ensure your API key is correct and the PDF contains readable text.")