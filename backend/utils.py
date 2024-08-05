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

def extract_info_from_text(text):
    # Dummy implementation for extracting information
    # You should replace this with actual parsing logic
    return {
        "projects": ["Project A", "Project B"],
        "education": ["University X", "University Y"]
    }
