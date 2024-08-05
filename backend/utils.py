import json
import fitz  # PyMuPDF

def load_resume(file):
    resume = json.load(file)
    return resume

def parse_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return extract_info_from_text(text)

import re

def extract_info_from_text(text):
    projects = re.findall(r'Project\s+[\w\s]+', text)
    education = re.findall(r'University\s+[\w\s]+', text)
    
    return {
        "projects": projects,
        "education": education
    }
