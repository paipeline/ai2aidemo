from pydantic import BaseModel, ValidationError
from openai import OpenAI
import json
import logging
from typing import Dict, List, Union, Any
from ai2aidemo.utils.pdf_parser import parse_pdf
from streamlit.runtime.uploaded_file_manager import UploadedFile

class ResumeJson(BaseModel):
    name: Any
    education: Any
    experience: Any
    skills: Any
    others: Any

class Agent:
    """
    The Agent class represents an individual entity capable of engaging in conversations,
    processing resume information, and generating responses based on its knowledge.
    """
    
    def __init__(self, resume_input: Union[dict, str, bytes, UploadedFile]):
        """
        Initializes the Agent with either a resume dict or PDF file.

        Parameters:
        ----------
        resume_input : Union[dict, str, bytes, UploadedFile]
            Either a dictionary containing structured resume data,
            or a PDF file (as bytes, file path, or Streamlit UploadedFile).
        """
        self.client = OpenAI()
        self.conversation_history = []
        
        # Process input and get resume dict
        if isinstance(resume_input, dict):
            resume_dict = resume_input
        elif isinstance(resume_input, UploadedFile):
            resume_dict = parse_pdf(resume_input)
            logging.info(f"Parsed Streamlit uploaded file")
        else:
            resume_dict = parse_pdf(resume_input)
            logging.info(f"Parsed file input")
        
        # Validate resume structure
        if not self._validate_resume_structure(resume_dict):
            raise ValueError("Invalid resume structure")
            
        # Continue with initialization
        self.resume = self._check_resume_json(resume_dict)
        self.name = self.resume.name
        self.enhanced_resume = self.get_enhanced()
        
        logging.info(f"Initialized agent for {self.name}")
        logging.debug(f"Enhanced resume: {self.enhanced_resume}")

    def get_name(self) -> str:
        """
        Returns the name of the agent.

        Returns:
        -------
        str
            The name of the agent.
        """
        return self.name

    def _check_resume_json(self, resume: dict) -> ResumeJson:
        """
        Validates the resume against the ResumeJson structure.

        Parameters:
        ----------
        resume : dict
            The resume information for the agent, passed as a dictionary.

        Returns:
        -------
        ResumeJson
            The validated resume in ResumeJson format.

        Raises:
        ------
        ValidationError
            If the resume does not match the ResumeJson format.
        """
        try:
            resume_json = ResumeJson(**resume)
            logging.debug("Resume is valid and matches the ResumeJson format.")
            return resume_json
        except ValidationError as e:
            logging.debug(f"Resume validation failed. Errors: {e.errors()}")
            raise

    def _validate_resume_structure(self, resume_dict: dict) -> bool:
        """Validates that the resume has all required fields with valid data."""
        required_fields = ['name', 'education', 'experience', 'skills', 'others']
        
        # Check all required fields exist
        for field in required_fields:
            if field not in resume_dict:
                logging.error(f"Missing required field: {field}")
                return False
            
            # Check that fields are not empty
            if not resume_dict[field]:
                logging.error(f"Empty required field: {field}")
                return False
        
        logging.info("Resume structure validation passed")
        return True

    def get_enhanced(self) -> dict:
        """
        Extracts relevant knowledge and insights from the resume and updates the knowledge attribute.

        Returns:
        -------
        dict
            Enhanced resume with additional insights generated using OpenAI.
        """
        insights = {}

        # Extract project descriptions from the resume
        projects = self.resume.projects if hasattr(self.resume, 'projects') else []
        detailed_projects = []
        
        if projects:
            for project in projects:
                prompt = f"""Extract detailed insights and key contributions from the following project description:\n\n{project}\n\nWhat are the most notable achievements and how do they impact the field?"""
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": """You are an expert in analyzing and summarizing project details in one text paragraph (no markdown)."""},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                detailed_projects.append({
                    "original_description": project,
                    "detailed_insights": response.choices[0].message.content
                })
        
        if detailed_projects:
            insights["detailed_projects"] = detailed_projects

        # Generate insights about skills
        skills = self.resume.skills if hasattr(self.resume, 'skills') else []
        if skills:
            prompt = f"Given the following skills: {', '.join(skills)}, what does this say about the individual's expertise and areas of specialization? What kind of roles or tasks would they excel in? Summarize in one paragraph."
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in analyzing professional skills and suggesting career paths. Write in one paragraph"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            insights["skills_insight"] = response.choices[0].message.content

        # Generate insights about experience
        experience = self.resume.experience if hasattr(self.resume, 'experience') else ""
        if experience:
            prompt = f"Based on the following experience: {experience}, what can you infer about this individual's strengths, leadership abilities, and potential career trajectory? Summarize in one paragraph"
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in evaluating professional experience and career growth. Summarize in one paragraph."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            insights["experience_insight"] = response.choices[0].message.content

        # Generate insights about education
        education = self.resume.education if hasattr(self.resume, 'education') else ""
        if education:
            prompt = f"Considering the following education background: {education}, what academic strengths or areas of expertise does this individual likely have?"
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": "You are an expert in evaluating educational backgrounds and academic strengths. Summarize in one paragraph."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            insights["education_insight"] = response.choices[0].message.content

        # Combine the original resume with the newly generated insights
        enhanced_resume = {**self.resume.dict(), **insights}
        
        # Return the enhanced resume with detailed project information and additional insights
        return enhanced_resume


    def inference(self, prompt: str) -> str:
        """Generates a response using the agent's knowledge."""
        system_prompt = f"""You are {self.name}, having a professional networking conversation.
        Resume: {json.dumps(self.enhanced_resume, indent=4)}
        
        Guidelines:
        - Be concise but informative
        - Use only information from your resume
        - Clearly indicate when sharing general industry insights
        - Focus on potential collaborations and knowledge exchange
        - Keep responses under 100 words"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def update_knowledge(self, new_info: dict):
        """
        Updates the agent's knowledge with new information extracted during the conversation.

        Parameters:
        ----------
        new_info : dict
            New information to be added to the agent's knowledge.
        """
        self.enhanced.update(new_info)

    def introduce(self):
        prompt = """Briefly introduce yourself, highlighting your key professional experiences and skills."""
        return self.inference(prompt)
    
    def respond_and_critique(self, last_message):
        prompt = f"""Regarding: "{last_message} concisely"
        1. Acknowledge their points
        2. Share a relevant experience
        3. Suggest a collaboration
        4. Ask one focused question
        
        Keep it casual."""
        
        return self.inference(prompt)

# Example usage
if __name__ == '__main__':
    resume = {
        "name": "Pai Eng",
        "education": {
            "degree": "Bachelor of Science",
            "major": "Computer Science",
            "university": "University of Barcelona"
        },
        "experience": "Software Engineer with 5 years of experience in AI and ML projects.",
        "skills": ["Python", "Machine Learning", "Deep Learning", "Data Science"],
        "projects": [
            "Developed an AI-based recommendation system for e-commerce platforms.",
            "Led a team in the creation of a machine learning model for predictive analytics in finance."
        ],
        "others": ["Certified AI Professional", "Published research papers"]
    }

    agent = Agent(resume=resume)
    logging.debug(f"Agent name: {agent.get_name()}")  # Output: Pai Eng
    logging.info(f"Agent resume: {agent.resume}")
    logging.debug(agent.get_enhanced())

