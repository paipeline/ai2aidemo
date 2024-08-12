from agent2 import Agent2
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List


class Message(BaseModel, ABC):
    """
    It takes three parameters: agent1 resumes, agent2 resumes, context, topics
    """
    agent1: Agent2
    agent2: Agent2

    def __init__(self, agent1: Agent2, agent2: Agent2):
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
    def __init__(self, agent1: Agent2, agent2: Agent2):
        super().__init__(agent1=agent1, agent2=agent2)
    
    def send_message(self, topic: str, context: List[str]):
        last_message = context[-1]
    
        context_str = "\n".join(context[:-1])
        prompt = (
            f"Agent {self.agent2.name}, here is the last message from {self.agent2.name} "
            f"and the context: {context_str}. Your task now is to give a question about "
            f"the topic: {topic} that combines your knowledge and his/her experiences."
        )

    


        return self.agent1.inference(prompt)
    
    
