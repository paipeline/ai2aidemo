import os
import sys
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
print(os.getcwd())
from abc import ABC, abstractmethod
from pydantic import BaseModel
from agent import Agent
from typing import List
from topics import Topics
from ai2aidemo.utils.pick_strategy import prob_based_pick

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Keep DEBUG level for console output
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

# Create a separate logger for INFO level messages
info_logger = logging.getLogger("info_logger")
info_logger.setLevel(logging.INFO)
info_handler = logging.FileHandler("info.log")
info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
info_logger.addHandler(info_handler)

class Message(BaseModel, ABC):
    class Config:
        arbitrary_types_allowed = True
    
    agent1: Agent
    agent2: Agent

    @abstractmethod
    def send_message(self, topic, conversation_history):
        pass
    
    @abstractmethod 
    def received_message(self, message):
        pass

import logging
from typing import List


class Question(Message):
    def send_message(self, topic: str, conversation_history: List[str]):
        logging.debug(f"Sending message with topic: {topic} and conversation_history: {conversation_history}")
        
        last_message = conversation_history[-1] if conversation_history else ""
        previous_conversation = "\n".join(conversation_history[:-1])

        resume_analysis_prompt = (
            f"""
            Analyze the following resume:
            {self.agent2.enhanced_resume}
            
            Identify key skills, experiences, and achievements relevant to the topic "{topic}".
            """
        )
        resume_analysis = self.agent1.inference(resume_analysis_prompt)
        logging.info(f"Resume Analysis: {resume_analysis}")

        conversation_analysis_prompt = (
            f"""
            Analyze the following conversation history:
            {previous_conversation}
            
            Identify the key themes and the direction of the conversation.
            """
        )
        conversation_analysis = self.agent1.inference(conversation_analysis_prompt)
        logging.info(f"Conversation Analysis: {conversation_analysis}")

        comment_prompt = (
            f"""Reflect on the last message from {self.agent2.name}: "{last_message}".
            Based on the conversation history and the resume analysis, provide a brief comment that acknowledges or adds value to the last message.
            """
        )
        brief_comment = self.agent1.inference(comment_prompt)
        logging.info(f"Generated comment: {brief_comment}")

        prompt = (
            f"""Here is the last message from your conversation: "{last_message}" from {self.agent2.name}, and the previous conversation: "{previous_conversation}".
            {self.agent2.name}'s resume: {resume_analysis}

            Generate a question about the topic "{topic}" that combines your knowledge, the other person's experiences, and the last message given.

            Examples:
            - "Given your experience with AI-driven applications, how do you see the role of AI evolving in {topic}?"
            - "With your background in computer science, what challenges do you foresee in upcoming years?"

            Format:
            Short, straightforward questions that transition smoothly. Ensure relevance to the topic and the last message given.

            Output limit:
            Less than 50 words.
            """
        )

        result = self.agent1.inference(prompt)
        logging.info(f"Generated Question - {self.agent1.name}: {result}")
        info_logger.info(f"Generated Question - {self.agent1.name}: {result}")  # Log to info.log

        final_response = f"{brief_comment} {result}"
        return final_response




    def received_message(self, message):
        message = "This is a mock received message."
        logging.debug(f"Received message: {message}")
        return message



class Response(Message):
    def send_message(self, topic: str, conversation_history: List[str]):
        logging.debug(f"Sending RESPONSE with topic: {topic}, conversation_history: {conversation_history}")
        
        if not conversation_history:
            raise ValueError("Need conversation_history before answering questions")
        
        last_message = conversation_history[-1]
        previous_conversation = "\n".join(conversation_history[:-1])
        
        resume_analysis_prompt = (
            f"""
            Analyze the following resume: 
            {self.agent2.enhanced_resume}
            
            Identify key skills, experiences, and achievements directly related to the topic "{topic}".
            """
        )
        resume_analysis = self.agent1.inference(resume_analysis_prompt)
        logging.info(f"Resume Analysis: {resume_analysis}")
        
        conversation_analysis_prompt = (
            f"""
            Analyze the following conversation history:
            {previous_conversation}
            
            Identify the key themes, concerns, and the direction of the conversation. Determine if the last message is a question or a comment.
            """
        )
        conversation_analysis = self.agent1.inference(conversation_analysis_prompt)
        logging.info(f"Conversation Analysis: {conversation_analysis}")
        
        response_type = "answer the question" if "?" in last_message else "build upon the previous comment"
        
        prompt = (
            f"""
            Using the following information:
            - Resume Analysis: {resume_analysis}
            - Conversation Analysis: {conversation_analysis}
            - Last Message: {last_message}
            
            Task:
            - If the last message was a question, use relevant knowledge from the resume and the conversation context.
            - If the last message was a comment, add new insights or valuable information that aligns with the documented experiences. Connect smoothly to the previous point.

            Examples:
            - "Yes, so AI-driven robotic surgery systems, like the Da Vinci Surgical System, are increasingly being adopted in healthcare. These systems enhance surgical precision, reduce recovery times, and are particularly beneficial in complex procedures like cardiac and neurosurgery."
            - "You're absolutely right. In addition, The integration of AI with advanced MRI techniques, such as diffusion tensor imaging (DTI), is improving the early detection of neurological disorders like Alzheimer’s and multiple sclerosis. This trend is enabling more personalized and timely treatment plans, significantly impacting patient outcomes."

            Format:
            Provide a short and direct response relevant to the last message. Stay concise and ensure the response feels like a natural continuation.

            Tone:
            Keep the tone conversational and avoid repetitive phrases like "Absolutely."

            Output limit:
            Less than 70 words.
            """
        )
        result = self.agent1.inference(prompt)
        logging.info(f"Generated Response - {self.agent1.name}: {result}")
        info_logger.info(f"Generated Response - {self.agent1.name}: {result}")  # Log to info.log
        return result


    def received_message(self, message):
        message = "This is a mock received message."
        logging.debug(f"Received message: {message}")
        return message




class Greeting(Message):
    def send_message(self, topic):
        logging.debug(f"Sending GREETING with topic: {topic}")
        
        # Generate a greeting prompt based on agent's resume
        prompt = (
            f"""
            Imagine you are {self.agent1.resume.name}, a professional with experience in {self.agent1.resume.experience}.
            You are meeting {self.agent2.resume.name} for the first time. Write a friendly and professional greeting that introduces yourself and mentions your mutual interest in {topic}.
            
            example:
            "Hi {self.agent2.resume.name}, it's great to meet you! I'm {self.agent1.resume.name}, a Software Engineer with a passion for AI. I’m really looking forward to our conversation, especially since we both have a strong background in AI and machine learning. Let's dive in!"

            format:
            The greeting should be brief, welcoming, and should set a positive tone for the conversation.
            
            output limit:
            less than 50 words
            """
        )
        
        result = self.agent1.inference(prompt)
        logging.info(f"Generated greeting - {self.agent1.name}: {result}")
        info_logger.info(f"Generated greeting - {self.agent1.name}: {result}")  # Log to info.log
        return result

    def received_message(self, message):
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

    #### Topic picker ####
    topics_generator = Topics(agent1_knowledge=resume1, agent2_knowledge=resume2)
    topic = prob_based_pick(topics_generator.generate_conversation_topics())
    
    conversation_history = []
    phone1 = '608-407-2501'
    phone2 = '607-407-2341'
    #### Greeting ####
    agent1 = Agent(resume1,phone1)
    agent2 = Agent(resume2,phone2)
    greeting = Greeting(agent1 =agent1, agent2=agent2)
    generated_greeting = greeting.send_message(topic=topic)
    conversation_history.append(generated_greeting)
    



    #### Question ####
    question = Question(agent1=agent1, agent2=agent2)
    # Define a topic and conversation_history
    generated_question = question.send_message(topic=topic, conversation_history=conversation_history)
    conversation_history.append(generated_question)


    #### Response ####
    response = Response(agent1=agent1, agent2=agent2)
    generated_response = response.send_message(topic=topic, conversation_history=conversation_history)



