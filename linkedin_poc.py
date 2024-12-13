import streamlit as st
from PyPDF2 import PdfReader
import spacy
import os
os.environ['OPENAI_API_KEY'] = 'Your_API_KEY')
from sentence_transformers import SentenceTransformer, util
from openai import OpenAI


# OpenAI API Key
OpenAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client
client = OpenAI(api_key=OpenAI_API_KEY)

# Initialize NLP model
nlp = spacy.load('en_core_web_sm')

# Initialize Sentence Transformers model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def extract_text_from_pdf(file):
    """Extract text from a PDF file."""
    pdf_reader = PdfReader(file)
    text = "".join([page.extract_text() for page in pdf_reader.pages])
    return text

def analyze_resume(resume_text):
    """Extract insights from a resume."""
    doc = nlp(resume_text)
    skills = [ent.text for ent in doc.ents if ent.label_ == 'SKILL']
    summary_prompt = f"Summarize the following skills: {resume_text}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": summary_prompt
        }],
        max_tokens=300
    )
    summary = response.choices[0].message.content
    return {"skills": skills, "summary": summary}


def analyze_job_description(jd_text):
    """Extract key requirements from a job description."""
    jd_text = f"Summarize the key skills, qualifications, and requirements from this job description:{jd_text}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": jd_text
        }],
        max_tokens=300
    )
    jd_analysis = response.choices[0].message.content
    return jd_analysis


def calculate_fit(resume_summary, job_description):
    # Encode the resume summary and job description
    resume_embedding = model.encode(resume_summary)
    jd_embedding = model.encode(job_description)

    # Calculate cosine similarity
    similarity_score = util.pytorch_cos_sim(resume_embedding, jd_embedding).item()

    # Convert to percentage and round to 2 decimal places
    return round(similarity_score * 100, 2)

def generate_recommendations(resume_text, jd_text, similarity_score):
    """Provide detailed feedback and recommendations based on the analysis."""
    prompt = f"""Analyse the resume and job description:
    Resume Summary: {resume_text}
    Job Description Analysis: {jd_text}
    Fit Score: {similarity_score}
    Provide: 
    - How the candidate fits the role.
    - Missing skills or experience required.
    - Steps to improve their chances
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        max_tokens=1000
    )
    recommendations = response.choices[0].message.content
    return recommendations
#Streamlit UI

st.title("AI-powered Job Description Assessment")
st.write("This AI tool helps assess a candidate's suitability for a job based on their resume and job description.")

#Upload files

uploaded_resume = st.file_uploader("Upload your resume as a PDF", type=["pdf"])
uploaded_jd = st.file_uploader("Upload your job description as a PDF", type=["pdf"])

if uploaded_resume and uploaded_jd:
    resume_text = extract_text_from_pdf(uploaded_resume)
    jd_text = extract_text_from_pdf(uploaded_jd)

    #Analyze resume
    st.subheader("Resume Analysis")
    resume_insights = analyze_resume(resume_text)
    st.write("**Extracted Skills:**", resume_insights["skills"])
    st.write("**Resume Summary:**", resume_insights["summary"])

    # Job Description Analysis
    st.subheader("Job Description Analysis")
    jd_analysis = analyze_job_description(jd_text)
    st.write("**Key Requirements:**", jd_analysis)

    # Calculate Fit Score
    st.subheader("Fit Score")
    similarity_score = calculate_fit(resume_insights["summary"], jd_analysis)
    st.write("**Fit Score:**", similarity_score)

    # Generate Recommendations
    st.subheader("Recommendations")
    recommendations = generate_recommendations(resume_text, jd_text, similarity_score)
    st.write("**Detailed Recommendations:**", recommendations)


