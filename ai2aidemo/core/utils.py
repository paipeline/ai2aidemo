import PyPDF2
import json

def parse_pdf(pdf_file):
    """
    Parse PDF file and extract text content.
    Returns a dictionary with basic resume structure.
    """
    # Read PDF file
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    # Create a basic resume structure
    # Note: In a real application, you'd want to use more sophisticated parsing
    resume = {
        "name": "AI Agent",  # You might want to extract this from the PDF
        "education": text[:200],  # First 200 characters for education
        "experience": text[200:600],  # Next 400 characters for experience
        "skills": text[600:800],  # Next 200 characters for skills
        "others": text[800:]  # Rest for other information
    }
    
    return resume

def load_resume(file_path):
    """
    Load resume from JSON file.
    """
    with open(file_path, 'r') as f:
        return json.load(f) 