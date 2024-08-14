from pydantic import BaseModel, ValidationError
from openai import OpenAI
import json
import logging
class ResumeJson(BaseModel):
    name: str
    education: dict
    experience: str
    skills: list[str]
    others: list[str]

class Agent:
    """
    The Agent class represents an individual entity capable of engaging in conversations,
    processing resume information, and generating responses based on its knowledge.

    Attributes:
    ----------
    conversation_history : list
        Stores the history of the conversation as a list of strings.
    name : str
        The name of the agent.
    resume : dict
        The resume information for the agent, passed as a dictionary.
    knowledge : dict
        Extracted knowledge from the resume, also stored as a dictionary.

    Methods:
    -------
    __init__(resume: dict)
        Initializes the Agent with a resume, extracts the name from the resume,
        and processes the resume to extract knowledge.
    
    get_name() -> str
        Returns the name of the agent.
    
    _check_resume_json(resume: dict) -> ResumeJson
        Validates the resume against the ResumeJson structure.
    
    get_enhanced(resume: dict) -> dict
        Extracts relevant knowledge from the resume and updates the knowledge attribute.
    
    inference(prompt: str) -> str
        Generates a response based on the given prompt by interacting with the GPT-4o-mini model.
    
    update_knowledge(new_info: dict)
        Updates the agent's knowledge with new information extracted during the conversation.
    
    load_resume(resume: dict)
        Loads a new resume into the agent, updates the resume attribute, and refreshes the knowledge attribute.
    """
    
    def __init__(self, resume: dict):#TODO v1 load in userId
        """
        Initializes the Agent with a resume. Extracts the name from the resume,
        and processes the resume to extract knowledge.

        Parameters:
        ----------
        resume : dict
            The resume information for the agent, passed as a dictionary.
        """
        self.conversation_history = []  # Stores the history of the conversation as a list of strings
    
        #TODO v1 wrap the initialization of agent with method: load_from_database()
        self.resume = self._check_resume_json(resume)  # Validate and store the resume in json format
        self.name = self.resume.name  # Extract the name from the validated resume
        self.enhanced_resume = self.get_enhanced()  # Extracted knowledge from the resume, also stored as a dictionary
        
        print(self.enhanced_resume)
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



    def get_enhanced(self) -> dict:
        """
        Extracts relevant knowledge and insights from the resume and updates the knowledge attribute.

        Returns:
        -------
        dict
            Enhanced resume with additional insights generated using OpenAI.
        """
        client = OpenAI()
        
        insights = {}

        # Extract project descriptions from the resume
        projects = self.resume.projects if hasattr(self.resume, 'projects') else []
        detailed_projects = []
        
        if projects:
            for project in projects:
                prompt = f"""Extract detailed insights and key contributions from the following project description:\n\n{project}\n\nWhat are the most notable achievements and how do they impact the field?"""
                
                response = client.chat.completions.create(
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
            
            response = client.chat.completions.create(
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
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in evaluating professional experience and career growth. Summarize in one paragraph."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            insights["experience_insight"] = response.choices[0].message.content

        # Generate insights about education
        education = self.resume.education if hasattr(self.resume, 'education') else {}
        if education:
            education_details = ', '.join([f"{key}: {value}" for key, value in education.items()])
            prompt = f"Considering the following education background: {education_details}, what academic strengths or areas of expertise does this individual likely have?"
            
            response = client.chat.completions.create(
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
        """
        Generates a response based on the given prompt by interacting with the GPT-4o-mini model.

        Parameters:
        ----------
        prompt : str
            The prompt or question to generate a response for.

        Returns:
        -------
        str
            The generated response.
        """
        client = OpenAI()
        system_prompt = f"""You are role playing {self.name} and networking with another amigable person.
        Here is your resume information: {json.dumps(self.enhanced_resume, indent=4)}.
        Respond at best of your ability combining the resume knowledge, your personal experience and the domain knowledge to give a thoughtful response.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        logging.debug("inference...")
        #TODO catch out of maxtoken.
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

