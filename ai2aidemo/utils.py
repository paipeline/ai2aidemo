import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from io import BytesIO
import json

def load_resume(file):
    resume = json.load(file)
    return resume

def parse_pdf(file):
    # Use fitz.Document to open the PDF document
    doc = fitz.Document(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    if not text.strip():  # If no text was extracted, try OCR
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.open(BytesIO(pix.tobytes()))
            text += pytesseract.image_to_string(img)
        print(f'OCR extracted text: {text}')  # Print the OCR extracted text
    return text.strip() if text.strip() else ""  # Ensure it always returns a string

import re

def extract_info_from_text(text):
    projects = re.findall(r'Project\s+[\w\s]+', text)
    education = re.findall(r'University\s+[\w\s]+', text)

    return {
        "projects": projects,
        "education": education
    }
