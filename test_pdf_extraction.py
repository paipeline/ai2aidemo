import unittest
from backend.utils import parse_pdf

class TestPDFExtraction(unittest.TestCase):
    def test_parse_pdf(self):
        with open('/Users/a23675/Desktop/resume final/resume Pai Eng.pdf', 'rb') as file:  
            extracted_text = parse_pdf(file)
            self.assertIsInstance(extracted_text, str)  # Check if the result is a string
            self.assertGreater(len(extracted_text), 0)  # Ensure that some text was extracted

if __name__ == '__main__':
    unittest.main()
