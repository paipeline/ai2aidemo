from pydantic import BaseModel, ValidationError
from openai import OpenAI
import json
import logging
from typing import Dict, List, Union, Any
from ai2aidemo.utils.pdf_parser import parse_pdf
from streamlit.runtime.uploaded_file_manager import UploadedFile
from ai2aidemo.core.schema import CharacterProfile, RolePlayInput, ResumeBase
from ai2aidemo.utils.text_parser import TextParser

class Agent:
    """
    The Agent class represents an individual entity capable of engaging in conversations,
    processing resume information, and generating responses based on its knowledge.
    """
    
    def __init__(self, input_data: Union[dict, str, bytes, 'UploadedFile', RolePlayInput]):
        """
        Initializes the Agent with either a resume dict or PDF file.

        Parameters:
        ----------
        input_data : Union[dict, str, bytes, UploadedFile, RolePlayInput]
            Either a dictionary containing structured resume data,
            or a PDF file (as bytes, file path, or Streamlit UploadedFile),
            or a role play input (as RolePlayInput).
        """
        self.client = OpenAI()
        self.conversation_history = []
        self.enhanced_resume = {}  # Initialize empty dict
        
        # Process input based on type
        if isinstance(input_data, RolePlayInput):
            parser = TextParser()
            self.profile = parser.parse_roleplay_to_profile(input_data)
            self.name = self.profile.name
            self.is_resume_based = False
        else:
            # Handle PDF resume case
            resume_dict = parse_pdf(input_data) if not isinstance(input_data, dict) else input_data
            if not self._validate_resume_structure(resume_dict):
                raise ValueError("Invalid resume structure")
            self.resume = ResumeBase(**resume_dict)
            self.name = self.resume.name
            self.is_resume_based = True
            self.enhanced_resume = self.get_enhanced()
        
        logging.info(f"Initialized agent for {self.name}")

    def get_name(self) -> str:
        """
        Returns the name of the agent.

        Returns:
        -------
        str
            The name of the agent.
        """
        return self.name

    def _check_resume_json(self, resume: dict):
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
        Extracts relevant knowledge and insights from the resume.
        Only called for resume-based agents.
        """
        if not self.is_resume_based:
            return {}
            
        insights = {}
        resume_dict = self.resume.dict()

        # Extract project descriptions
        projects = resume_dict.get('projects', [])
        detailed_projects = []
        
        if projects:
            for project in projects:
                prompt = f"""Extract detailed insights and key contributions from the following project description:\n\n{project}\n\nWhat are the most notable achievements and how do they impact the field?"""
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert in analyzing and summarizing project details in one text paragraph (no markdown)."},
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
        skills = resume_dict.get('skills', [])
        if skills:
            prompt = f"Given the following skills: {', '.join(skills)}, what does this say about the individual's expertise and areas of specialization?"
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in analyzing professional skills. Write in one paragraph."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            insights["skills_insight"] = response.choices[0].message.content

        # Generate insights about experience
        experience = resume_dict.get('experience', '')
        if experience:
            prompt = f"Based on the following experience: {experience}, what can you infer about this individual's strengths and abilities?"
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in evaluating professional experience. Summarize in one paragraph."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            insights["experience_insight"] = response.choices[0].message.content

        # Combine original resume with insights
        enhanced_resume = {**resume_dict, **insights}
        return enhanced_resume

    def inference(self, prompt: str) -> str:
        """Generates a response using the agent's knowledge."""
        if self.is_resume_based:
            system_prompt = f"""You are {self.name}, having a professional networking conversation.
            Background: {json.dumps(self.enhanced_resume, indent=4)}
            
            Guidelines:
            - Express both agreements and disagreements thoughtfully
            - Support your views with your experience
            - Build on shared perspectives when possible
            - Respectfully present alternative viewpoints
            - Keep responses under 100 words"""
        else:
            system_prompt = f"""You are {self.name}, engaging in a literary discussion.
            Profile:
            - Background: {self.profile.background}
            - Interests: {', '.join(self.profile.interests)}
            - Knowledge Areas: {', '.join(self.profile.knowledge_areas)}
            - Personality: {self.profile.personality or 'Not specified'}
            
            Guidelines:
            - Stay true to your literary style and perspective
            - Find common ground while maintaining your unique voice
            - Share insights from your works and experiences
            - Engage with both similar and different viewpoints
            - Express disagreements with grace and depth
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
        """Updates the agent's knowledge with new information."""
        if self.is_resume_based:
            self.enhanced_resume.update(new_info)
        else:
            # Could implement knowledge update for character-based agents if needed
            pass

    def introduce(self):
        if self.is_resume_based:
            prompt = """Introduce yourself warmly, sharing your perspective and experiences while showing openness to dialogue."""
        else:
            prompt = """Introduce yourself as a literary figure, expressing your unique worldview while inviting intellectual exchange."""
        return self.inference(prompt)
    
    def respond_and_critique(self, last_message):
        prompt = f"""Regarding: "{last_message}"
        1. Acknowledge points of agreement
        2. Share a related perspective or experience
        3. Express any differing viewpoints respectfully
        4. Ask an engaging follow-up question
        
        Balance agreement and disagreement in your response, staying true to your character."""
        
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

