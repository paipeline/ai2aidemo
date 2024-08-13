from agent2 import Agent
import logging
import logging
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Message(BaseModel, ABC):
    class Config:
        arbitrary_types_allowed = True
    """
    It takes three parameters: agent1 resumes, agent2 resumes, context, topics
    """
    agent1: Agent
    agent2: Agent
    @abstractmethod
    def send_message(self,topic,context):
        pass
    
    @abstractmethod 
    def received_message(self):
        pass

class Question(Message):
    """_summary_

    Args:
        ABC (_type_): _description_
    """
    
    def send_message(self, topic: str, context: List[str]):
        """
            send question
        """
        logging.debug(f"Sending message with topic: {topic} and context: {context}")
        logging.debug(f"Sending message with topic: {topic} and context: {context}")
        # separate the context and the last message
        last_message = context[-1]

        context_str = "\n".join(context[:-1])
        prompt = (
            f"Agent {self.agent2.name}, here is the last message from {self.agent2.name} "
            f"and the context: {context_str}. Your task now is to give a question about "
            f"the topic: {topic} that combines your knowledge and his/her experiences."
        )

        result = self.agent1.inference(prompt)
        logging.debug(f"Generated question: {result}")
        return result

    def received_message(self):
        # Mock implementation for demonstration purposes
        message = "This is a mock received message."
        logging.debug(f"Received message: {message}")
        return message


    
    
if __name__ == "__main__":    
    resume1 = {
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




    resume2 = {
        "name": "Alex Martinez",
        "education": {
            "degree": "Bachelor of Engineering",
            "major": "Software Engineering",
            "university": "Polytechnic University of Valencia"
        },
        "experience": "Software Developer with 5 years of experience in AI and ML applications.",
        "skills": ["Java", "Artificial Intelligence", "Neural Networks", "Data Engineering"],
        "projects": [
            "Created an AI-powered chatbot for customer service automation.",
            "Spearheaded the development of a neural network model for real-time image recognition."
        ],
        "others": ["Certified Machine Learning Specialist", "Authored multiple technical articles"]
    }


                                                                                                                                                                                        
    agent1 = Agent(resume1)                                                                                                                                                                                                    
    agent2 = Agent(resume2)                                                                                                                                                                                                    
                                                                                                                                                                                                                            
    # Create an instance of Question                                                                                                                                                                                           
    question = Question(agent1=agent1, agent2=agent2)                                                                                                                                                                          
                                                                                                                                                                                                                            
    # Define a topic and context                                                                                                                                                                                               
    topic = "Artificial Intelligence"                                                                                                                                                                                          
    context = [                                                                                                                                                                                                                
        "AI is a branch of computer science.",                                                                                                                                                                                 
        "It involves the creation of intelligent agents.",                                                                                                                                                                     
        "These agents can perform tasks that typically require human intelligence.",                                                                                                                                           
        "The last message in the context."                                                                                                                                                                                     
    ]                                                                                                                                                                                                                          
    print(context)                                                                                                                                                                                  
    # Use the send_message method to generate a question                                                                                                                                                                       
    generated_question = question.send_message(topic=topic, context=context)                                                                                                                                                   
                                                                                                                                                                                                                            
    # Print the generated question                                                                                                                                                           
    logging.debug(f"Generated question in mock:{generated_question}")                                                                                                                                                                                 
    print(generated_question)
