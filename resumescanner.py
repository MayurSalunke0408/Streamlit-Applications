import streamlit as st
import pandas as pd
import re
from io import StringIO, BytesIO
import PyPDF2
from docx import Document

# Function to extract text from PDF
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file):
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Function to parse resume details
def parse_resume(text):
    details = {}
    
    # Extract name (Assuming first line might be the name)
    details['Name'] = text.split("\n")[0].strip()
    
    # Extract email
    email = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    details['Email'] = email[0] if email else 'N/A'
    
    # Extract phone number
    phone = re.findall(r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
    details['Phone'] = phone[0] if phone else 'N/A'
    
    # Extract skills (simple example using keywords)
    skills_keywords = ['Python', 'SQL', 'Excel', 'Machine Learning', 'Data Analysis', 'Java', 'R']
    found_skills = [skill for skill in skills_keywords if skill.lower() in text.lower()]
    details['Skills'] = ", ".join(found_skills) if found_skills else 'N/A'
    
    # Extract years of experience (Example assumes format: 'X years')
    experience = re.findall(r'\b\d+\s+years?\b', text)
    details['Experience'] = experience[0] if experience else 'N/A'
    
    return details

# Streamlit app
st.title("Resume Parser Application")

uploaded_files = st.file_uploader("Upload Resumes (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    data = []
    for uploaded_file in uploaded_files:
        # Extract text based on file type
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(uploaded_file)
        else:
            st.error(f"Unsupported file type: {uploaded_file.type}")
            continue
        
        # Parse resume details
        details = parse_resume(text)
        details['File Name'] = uploaded_file.name  # Add file name for reference
        data.append(details)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Display the extracted data
    st.write("Extracted Information:")
    st.dataframe(df)
    
    # Download the data as Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Resume Data")
    st.download_button(
        label="Download Data as Excel",
        data=output.getvalue(),
        file_name="Resume_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
