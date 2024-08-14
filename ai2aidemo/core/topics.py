import logging
from openai import OpenAI
from typing import List
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from ai2aidemo.utils.pick_strategy import prob_based_pick

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Topics:
    """
    The Topics class generates likely topics of conversation based on the knowledge and experience
    of two agents. It uses OpenAI's language model to directly identify commonalities and refine
    these into conversation topics related to networking.

    Attributes:
    ----------
    agent1_knowledge : dict
        The knowledge and experience information for agent 1.
    agent2_knowledge : dict
        The knowledge and experience information for agent 2.

    Methods:
    -------
    __init__(agent1_knowledge: dict, agent2_knowledge: dict)
        Initializes the Topics class with knowledge and experience of two agents.
    
    generate_conversation_topics() -> list[str]
        Uses OpenAI to identify commonalities between the agents and generate refined conversation topics.
    """

    def __init__(self, agent1_knowledge: dict, agent2_knowledge: dict):
        """
        Initializes the Topics class with knowledge and experience of two agents.
        Parameters:
        ----------
        agent1_knowledge : dict
            The knowledge and experience information for agent 1.
        agent2_knowledge : dict
            The knowledge and experience information for agent 2.
        """
        self.agent1_knowledge = agent1_knowledge
        self.agent2_knowledge = agent2_knowledge
        logging.debug(f"Initialized Topics with agent1_knowledge: {agent1_knowledge} and agent2_knowledge: {agent2_knowledge}")

    def generate_conversation_topics(self) -> List[str]:
        """
        Uses OpenAI to identify commonalities between the agents and generate refined conversation topics.

        Returns:
        -------
        List[str]
            A list of refined conversation topics.
        """
        client = OpenAI()
        
        # Construct a prompt that provides both agents' knowledge and asks AI to find commonalities and suggest networking-related topics
        prompt = (
            f"Given the following background information for two individuals, identify commonalities in their knowledge, "
            f"skills, and experience, and suggest specific topics of conversation that would be interesting for professional networking:\n\n"
            f"Agent 1 Knowledge: {self.agent1_knowledge}\n\n"
            f"Agent 2 Knowledge: {self.agent2_knowledge}\n\n"
            f"Please provide a list of one-line networking-focused very specific conversation topics. Produce 5 elements for the list, do not enumerate, or any unnecessary leading characters.\n\n"
            f"Examples: \n"
            f"Production-Level AI Deployment\n"
            f"Python Data Tools (Pandas, NumPy, Scikit-learn)\n"
            f"AI-Driven Software Solutions\n\n"
            f"Format: List[str]"
        )

        logging.debug(f"Generated prompt for OpenAI: {prompt}")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in generating networking-focused conversation topics based on shared knowledge and experience."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Debugging the response from OpenAI
        logging.debug(f"Received response from OpenAI: {response}")

        # Extract and return the list of topics from the AI's response
        topics = response.choices[0].message.content

        # Split the response into lines and clean up any extraneous characters
        topic_list = [topic.strip() for topic in topics.split("\n") if topic.strip()]
        
        logging.debug(f"Extracted topics: {topic_list}")

        return topic_list


# Example usage:
if __name__ == '__main__':
    # Example knowledge dictionaries for two agents
    agent1_knowledge = {
        "skills": ["Python", "Machine Learning", "Data Science"],
        "experience": "5 years in software engineering, specializing in AI and ML projects.",
        "education": {
            "degree": "Bachelor of Science",
            "major": "Computer Science",
            "university": "University of AI"
        },
    }

    agent2_knowledge = {
        "skills": ["Python", "Deep Learning", "Data Analysis"],
        "experience": "7 years in data science, with a focus on deep learning models.",
        "education": {
            "degree": "Bachelor of Engineering",
            "major": "Computer Engineering",
            "university": "Tech Institute"
        },
    }
    
    topics_generator = Topics(agent1_knowledge=agent1_knowledge, agent2_knowledge=agent2_knowledge)
    conversation_topics = topics_generator.generate_conversation_topics()
    topic = prob_based_pick(conversation_topics)
    print("topic been picked: ", topic)