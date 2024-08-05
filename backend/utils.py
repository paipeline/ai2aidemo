import json
import logging
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from io import BytesIO

def load_resume(file):
    resume = json.load(file)
    return resume

def parse_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
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
        logging.info(f'OCR extracted text: {text}')  # Log the OCR extracted text
        return extract_info_from_text(text)

import re

def extract_info_from_text(text):
    projects = re.findall(r'Project\s+[\w\s]+', text)
    education = re.findall(r'University\s+[\w\s]+', text)

    return {
        "original_text": text,
        "projects": projects,
        "education": education
    }
