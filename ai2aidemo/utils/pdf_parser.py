from PyPDF2 import PdfReader
from openai import OpenAI
import json
import logging
import re
import os

class ResumeParser:
    def __init__(self):
        self.client = OpenAI()
        self.default_resume = {
            "name": "Unknown Professional",
            "education": {
                "degree": "Unknown",
                "major": "Unknown",
                "university": "Unknown"
            },
            "experience": "Not available",
            "skills": ["No skills extracted"],
            "projects": [],
            "others": []
        }

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract raw text from PDF file."""
        try:
            reader = PdfReader(pdf_file)
            text = []
            for page in reader.pages:
                content = page.extract_text()
                if content.strip():
                    text.append(content.strip())
            
            full_text = "\n".join(text)
            if not full_text.strip():
                raise ValueError("Extracted text is empty")
            
            logging.info(f"Successfully extracted {len(full_text)} characters from PDF")
            return full_text.strip()
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    def extract_name(self, text: str) -> str:
        """Extract name from resume text using pattern matching and GPT validation."""
        try:
            # First try pattern matching for common name formats
            patterns = [
                r"^([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)",  # Name at start of resume
                r"Name:\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)",  # Explicit name field
                r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\b.*?(?:@|Phone|Address|Email)",  # Name near contact info
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    name = matches[0].strip()
                    logging.info(f"Found name using pattern matching: {name}")
                    return name
            
            # If pattern matching fails, use GPT to extract name
            prompt = f"""Extract the full name from this resume text. Return ONLY the name, nothing else.
            If you can't find a clear name, return 'Unknown Professional'.

            Resume text (first 1000 characters):
            {text[:1000]}"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a resume parser. Extract only the name."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            extracted_name = response.choices[0].message.content.strip()
            logging.info(f"Found name using GPT: {extracted_name}")
            return extracted_name if extracted_name != "Unknown" else "Unknown Professional"
            
        except Exception as e:
            logging.error(f"Error extracting name: {str(e)}")
            return "Unknown Professional"

    def structure_resume(self, text: str, name: str) -> dict:
        """Use GPT to structure the resume text into required JSON format."""
        try:
            logging.info(f"Structuring resume for {name}")
            
            # Split text into chunks if too long
            max_chunk_length = 4000
            text_chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
            
            prompt = f"""Analyze this resume text and create a JSON object with these EXACT fields:
            {{
                "name": "{name}",
                "education": {{
                    "degree": "string",
                    "major": "string",
                    "university": "string"
                }},
                "experience": "string summarizing work history",
                "skills": ["skill1", "skill2", ...],
                "projects": ["project1 description", "project2 description", ...],
                "others": ["certification1", "achievement1", ...]
            }}

            IMPORTANT RULES:
            1. Output ONLY the JSON object, no other text or markdown
            2. All fields must be present
            3. Use "Unknown" for missing text fields
            4. Use non-empty arrays even if just ["No items found"]
            5. Ensure valid JSON format
            6. Keep responses concise

            Resume text part 1:
            {text_chunks[0]}"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a resume parser that outputs only valid JSON objects. Never include markdown formatting or explanations."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )

            try:
                response_text = response.choices[0].message.content.strip()
                
                # Clean up the response
                response_text = response_text.replace('```json', '').replace('```', '').strip()
                
                logging.debug(f"GPT response: {response_text}")
                
                # Parse JSON with error handling
                try:
                    structured_resume = json.loads(response_text)
                except json.JSONDecodeError as e:
                    logging.error(f"Invalid JSON: {response_text}")
                    return self.default_resume

                # Validate and fix structure
                structured_resume = self.validate_resume_structure(structured_resume, name)
                
                logging.info("Successfully structured resume")
                return structured_resume
                
            except Exception as e:
                logging.error(f"Error processing GPT response: {str(e)}")
                return self.default_resume
                
        except Exception as e:
            logging.error(f"Error structuring resume: {str(e)}")
            return self.default_resume

    def validate_resume_structure(self, resume: dict, name: str) -> dict:
        """Validate and fix resume structure."""
        try:
            # Start with default structure
            validated_resume = self.default_resume.copy()
            
            # Update with parsed values, maintaining structure
            if isinstance(resume, dict):
                # Handle education
                if isinstance(resume.get('education'), dict):
                    validated_resume['education'].update({
                        k: str(v) for k, v in resume['education'].items()
                        if k in ['degree', 'major', 'university']
                    })
                
                # Handle experience
                if 'experience' in resume:
                    validated_resume['experience'] = str(resume['experience'])
                
                # Handle lists
                for field in ['skills', 'projects', 'others']:
                    if field in resume and isinstance(resume[field], list):
                        validated_resume[field] = [str(item) for item in resume[field] if item]
                    if not validated_resume[field]:  # Ensure non-empty arrays
                        validated_resume[field] = [f"No {field} found"]
                
            # Ensure name is set
            validated_resume['name'] = name
            
            return validated_resume
            
        except Exception as e:
            logging.error(f"Error validating resume structure: {str(e)}")
            return self.default_resume

def parse_pdf(pdf_file) -> dict:
    """Main function to parse PDF resume into structured format."""
    try:
        parser = ResumeParser()
        
        # Extract text from PDF
        text = parser.extract_text_from_pdf(pdf_file)
        if not text:
            raise ValueError("No text extracted from PDF")
            
        # Extract name first
        name = parser.extract_name(text)
        logging.info(f"Extracted name: {name}")
        
        # Structure the resume
        structured_resume = parser.structure_resume(text, name)
        logging.info(f"Structured resume: {json.dumps(structured_resume, indent=2)}")
        
        return structured_resume
        
    except Exception as e:
        logging.error(f"Error in parse_pdf: {str(e)}")
        return ResumeParser().default_resume