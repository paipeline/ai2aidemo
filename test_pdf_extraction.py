import unittest
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from io import BytesIO

class TestPDFExtraction(unittest.TestCase):
    def test_parse_pdf(self):
        with open('/Users/a23675/Desktop/resume final/resume Pai Eng.pdf', 'rb') as file:  
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
            extracted_text = text.strip() if text.strip() else ""  # Ensure it always returns a string
            print(extracted_text)
            self.assertIsInstance(extracted_text, str)  # Check if the result is a string
            self.assertGreater(len(extracted_text), 0)  # Ensure that some text was extracted

if __name__ == '__main__':
    unittest.main()
