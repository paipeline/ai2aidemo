from agent2 import Agent2
from abc import ABC, abstractmethod


class Message(ABC):
    """
    It takes three parameters: agent1 resumes, agent2 resumes, context, topics
    """
    def __init__(self, agent1,agent2):
        self.agent1 = agent1
        self.agent2 = agent2
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
    def __init__(self, agent1, agent2):
        super().__init__(agent1, agent2, context, topics)
    
    def send_message(self,topic:str,context: List):
        last_message = context[-1]
    
        prompt = f""" the agent: {self.agent2.name} here is the last message from {self.agent2.name} and the context: {context[:-1].join("/n")}  Your task now is to give a question about the topic: {topic} that combines your knowledge and his/her experiences"""

    


        return self.agent1.inference(prompt)
    
    
