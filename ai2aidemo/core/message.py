from agent import Agent
import logging
import logging
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("conversation.log"),
        logging.StreamHandler()
    ]
)


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
    def received_message(self,message):
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
        # separate the context and the last message
        last_message = context[-1]
        context_str = "\n".join(context[:-1])
        prompt = (
            f"""Here is the last message {last_message} from {self.agent2.name} and the previous conversation: {context_str}. You need to give a question about 
            the topic: {topic} that combines your knowledge, his/her experiences and the last message given"""
        )

        result = self.agent1.inference(prompt)
        logging.debug(f"Generated question: {result}")
        return result

    def received_message(self,message):
        # Mock implementation for demonstration purposes
        message = "This is a mock received message."
        logging.debug(f"Received message: {message}")
        return message

class Response(Message):
    """_summary_

    Args:
        ABC (_type_): _description_
    """
    
    def send_message(self,topic:str, context: List[str]):
        """
            send question
        """
        logging.debug(f"Sending RESPONSE with topic: {topic} and context: {context}")
        # separate the context and the last message
        last_message = context[-1] # could be either question or another response
        context_str = "\n".join(context[:-1])
        prompt = (
            f"""Here is the last message {last_message} from {self.agent2.name} and the previous conversation: {context_str}. You need to give a response about 
            the last message that combines your knowledge, his/her experiences and the last message given"""
        )
        result = self.agent1.inference(prompt)
        logging.debug(f"Generated question: {result}")
        return result

    def received_message(self,message):
        # Mock implementation for demonstration purposes
        message = "This is a mock received message."
        logging.debug(f"Received message: {message}")
        return message



if __name__ == "__main__":    
    resume1 = {
        "name": "Lucia Eng",
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

    ################################################
    ########### mock 1 cycle conversation ##########                                                                                              
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
    logging.debug(f"Context: {context}")
    # Use the send_message method to generate a question                                                                                                                                                                       
    generated_question = question.send_message(topic=topic, context=context)                                                                                                                                                   
                                                                                                                                                                                                                            
    # Print the generated question                                                                                                                                                           
    logging.debug(f"Generated question in mock:{generated_question}")                                                                                                                                                                                 
    logging.debug(f"Generated question in use_case: {generated_question}")
    context.append(generated_question)                                                                                                                                                                          
    print(context)                                                                                                                                        
    # Create an instance of Question                                                                                                                                                                                           
    response = Response(agent1=agent1, agent2=agent2)                                                                                                                                                                          

    logging.debug(f"Context: {context}")
    # Use the send_message method to generate a question                                                                                                                                                                       
    generated_response = response.send_message(topic=topic, context=context)                                                                                                                                                   
                                                                                                                                                                                                                            
    # Print the generated response                                                                                                                                                           
    logging.debug(f"Generated response in mock:{generated_response}")                                                                                                                                                                                 
    logging.debug(f"Generated response in use_case: {generated_response}")
