import unittest
import fitz  # PyMuPDF
import pytesseract
from backend.utils import load_resume
from io import BytesIO

class TestPDFExtraction(unittest.TestCase):
    def test_parse_pdf(self):
        with open('/Users/a23675/Desktop/resume final/resume Pai Eng.pdf', 'rb') as file:  
            extracted_text = load_resume(file)  # Use load_resume to extract text
            self.assertIsInstance(extracted_text, str)  # Check if the result is a string
            self.assertGreater(len(extracted_text), 0)  # Ensure that some text was extracted

if __name__ == '__main__':
    unittest.main()
