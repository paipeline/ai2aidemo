import os
import sys
import logging
from pydantic import BaseModel, Field, ValidationError
from typing import List, Callable
from topics import Topics
from agent import Agent
from message import Message, Question, Response, Greeting
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from ai2aidemo.utils.score import Score
from ai2aidemo.utils.pick_strategy import prob_based_pick
import random
# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Keep DEBUG level for console output
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("info.log"),
        logging.StreamHandler()
    ]
)

class Flow:
    def __init__(self, agent1: Agent, agent2: Agent):
        self.agent1 = agent1
        self.agent2 = agent2
        self.conversation_history = []
        self.scorer = Score()
        self.topic_lst = self._set_topics()
        self.topic = None
        self.sequence = []
        logging.info("Here are some topics:")
        logging.info(self.topic_lst)
        

    def __START__(self):
        """load agent info from the database"""
        pass

    def __CONDITION__(self):
        """Decide whether to explore or exploit."""
        # Calculate the exploitation probability based on conversation history and scores
        exploitation_probability = self.calculate_exploitation_probability()

        # Randomly choose between exploration and exploitation based on the probability
        if self.sequence[-1] == 1 and random.random() < exploitation_probability: # if the last action was a response
            logging.info("Exploration: Asking a new question.")
            return Question
        else: # if the last action was a question or when the condition suggests exploitation
            logging.info("Answering the previous question")
            return Response

            
    def calculate_exploitation_probability(self):
        """Calculate probability of exploitation based on current scores or other factors."""
        #TODO LEARN IT BY POLICY
        return 0.5


    def __END__(self):
        """provide ending score for the quality of the conversation and Add it the conversation to the database"""
        # Implement the logic for ending the conversation here
        pass
    
    def exchange(self, exchange_class: Callable, topic: str, sender: Agent, receiver: Agent) -> str:
        """
        Handles the conversation exchange between the two agents using the provided exchange class.

        Parameters:
        ----------
        exchange_class : Callable
            A class that handles a specific type of message exchange, such as Greeting, Response, or Question.
            The class must have a `send_message` method.
        
        topic : str
            The topic of the conversation.

        sender : Agent
            The agent sending the message.

        receiver : Agent
            The agent receiving the message.

        Returns:
        -------
        str
            The generated message from the exchange class.
        """
        if issubclass(exchange_class, Greeting):
            # Generate greeting from sender to receiver
            greeting_from_sender = f"{sender.name}: " + exchange_class(agent1=sender, agent2=receiver).send_message(topic)
            self.sequence.append(-1)
            self.conversation_history.append(greeting_from_sender)
            
            # Generate greeting from receiver back to sender
            greeting_from_receiver = f"{receiver.name}: " + exchange_class(agent1=receiver, agent2=sender).send_message(topic)
            self.sequence.append(-1)
            self.conversation_history.append(greeting_from_receiver)
            
            # Combine both greetings
            mutual_greeting = f"{greeting_from_sender}\n{greeting_from_receiver}"
            return mutual_greeting
            
        else:
            # Question and Response require history
            message = exchange_class(agent1=sender, agent2=receiver).send_message(topic, self.conversation_history)
            message = f"{sender.name}: {message}"
            # Record sequence of Question and Answer
            self.sequence.append(0 if issubclass(exchange_class, Question) else 1)
        
        # Log and update the conversation context
        logging.info(f"Generated message: {message}")
        self.conversation_history.append(message)
        
        # Return the generated message
        return message

    def get_overall_score(self) -> float:
        """Calculates the overall score for the conversation flow."""
        # Implement logic to calculate the overall score based on the conversation
        return 0.0

    def get_score_context(self) -> float:
        """Calculates the score based on context relevance."""
        # Implement logic to calculate the score based on context relevance
        return 0.0

    def get_score_bert(self) -> float:
        """Calculates the BERT score for the given message."""
        # Implement logic to calculate the BERT score using the Scorer instance
        return 0.0

    def _set_topics(self) -> Topics:
        """Set and return the list of user topics."""
        topics_generator = Topics(agent1_knowledge=self.agent1.enhanced_resume, agent2_knowledge=self.agent2.enhanced_resume)
        return topics_generator.generate_conversation_topics()


    def get_sequence(self) -> List[int]:
        """Returns the sequence of GQR."""
        return self.sequence


    def iter(self):
        """Executes the conversation flow."""
        self.topic = prob_based_pick(self.topic_lst) # eliminiate topic_lst inplace
        ## init ##
        generated_greetings = self.exchange(Greeting,self.topic,self.agent1,self.agent2)

        generated_question = self.exchange(Question, self.topic, self.agent1, self.agent2)
        generated_response = self.exchange(Response,self.topic, self.agent2, self.agent1)
            
        for _ in range(6):
            if (len(self.sequence) % 2 == 1):
                primary_agent = self.agent1
                secondary_agent = self.agent2
            else:
                primary_agent = self.agent2
                secondary_agent = self.agent1

            next_action = self.__CONDITION__()
            if next_action == Question:
                generated_question = self.exchange(Question,self.topic,primary_agent,secondary_agent)
            else:
                generated_response = self.exchange(Response,self.topic,primary_agent,secondary_agent)
            
                
            logging.info(f"Current topic: {self.topic}")
        
        # Log the sequence to info.log instead of printing
        logging.info(f"Sequence of GQR: {self.sequence}")


if __name__ == "__main__":
    resume1 = {
        "name": "Pai Eng",
        "education": {"degree": "Bachelor of Science", "major": "Computer Science", "university": "University of Barcelona"},
        "experience": "Software Engineer with 5 years of experience in AI and ML projects.",
        "skills": ["Python", "Machine Learning", "Deep Learning", "Data Science"],
        "projects": ["Developed an AI-based recommendation system for e-commerce platforms.", "Led a team in the creation of a machine learning model for predictive analytics in finance."],
        "others": ["Certified AI Professional", "Published research papers"]
    }

    resume1 = {
        "name": "Emily Zhang",
        "education": {
            "degree": "Doctor of Medicine (MD)",
            "major": "Medicine",
            "university": "Harvard Medical School",
            "graduation_year": "2023"
        },
        "experience": "Doctor with 1 year of experience, currently working at MedCare Group, a leading healthcare provider known for delivering high-quality patient care.",
        "skills": ["Clinical Diagnostics", "Patient Care", "Emergency Medicine", "Chronic Disease Management"],
        "projects": [
            "Led a patient care initiative in the cardiology department, improving patient recovery times by 15%.",
            "Conducted research on the effectiveness of traditional treatment methods for chronic conditions, contributing to a study published in a medical journal."
        ],
        "others": [
            "Licensed Physician in the State of Massachusetts",
            "Member of the American Medical Association (AMA)",
            "Certified in Advanced Cardiovascular Life Support (ACLS)"
        ]
    }



    
    resume2 = {
        "name": "Chong Chen",
        "education": [
            {
                "degree": "Bachelor of Science",
                "major": "Computer Sciences",
                "university": "University of Wisconsin-Madison",
                "gpa": "4.00/4.00",
                "location": "Madison, WI",
                "dates": "Aug. 2023 – Dec. 2024"
            },
            {
                "degree": "Bachelor of Science",
                "major": "Computer Engineering",
                "university": "The Ohio State University",
                "gpa": "3.74/4.00",
                "location": "Columbus, OH",
                "dates": "Aug. 2021 – May 2023"
            }
        ],
        "experience": [
            {
                "title": "Software Developer Intern",
                "company": "Shanghai MaiMiao Internet Ltd.",
                "location": "Remote",
                "dates": "May 2024 - Present",
                "responsibilities": [
                    "Designed and developed a scalable, full-stack mobile app with React Native + Expo and Spring Boot + Java microservices, enhancing UX and business operations.",
                    "Implemented efficient RESTful APIs and a flexible message service interface, optimizing system performance by 30% and enabling integration with various backends.",
                    "Set up a CI/CD pipeline automating builds, tests, and deployments, reducing manual efforts by 80% and accelerating releases by 50%, ensuring code quality.",
                    "Conducted code reviews, maintained documentation, and mentored junior developers, promoting best practices and collaboration."
                ]
            },
            "Worked as a freelance developer, building various applications for clients."
        ],
        "skills": "Proficient in Python, Java, and C#",
        "others": "Additional information not structured"
    }

    # resume2 = {
    #     "name": "Alex Martinez",
    #     "education": {"degree": "Bachelor of Engineering", "major": "Software Engineering", "university": "Polytechnic University of Valencia"},
    #     "experience": "Software Developer with 5 years of experience in AI and ML applications.",
    #     "skills": ["Java", "Artificial Intelligence", "Neural Networks", "Data Engineering"],
    #     "projects": ["Created an AI-powered chatbot for customer service automation.", "Spearheaded the dvelopment of a neural network model for real-time image recognition."],
    #     "others": ["Certified Machine Learning Specialist", "Authored multiple technical articles"]
    # }

    agent1 = Agent(resume1)
    agent2 = Agent(resume2)

    flow = Flow(agent1=agent1, agent2=agent2)
    flow.iter()  # Execute the conversation flow
    print(flow.conversation_history)



#### FUTURE WORK ON THE SEQUENCE ####

# Each pairs of question and answer or answer and answer will have a score retrieval metric associated with calculated by bert, similarity score
# -1 0 1 0 1 1 1 0 1 0 1 (associated) ->  0.8, 0.6, 0.4, 0.6, 0.8 | 9 (conversation score GPT on the content) | 4 (human score on the context)
# -1 0 1 1 1 0 1 0 1 0 1 (associated) ->  0.1, 0.4, 0.2, 0.5, 0.9 | 4 (conversation score GPT on the content) | 9 (human score on the context)
# if the convesation 
# We want to learn the parameters for when __CONDITION__ function to determine when to change topic and how much more information to add