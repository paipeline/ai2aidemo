from agent2 import Agent
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List


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
        # separate the context and the last message
        last_message = context[-1]

        context_str = "\n".join(context[:-1])
        prompt = (
            f"Agent {self.agent2.name}, here is the last message from {self.agent2.name} "
            f"and the context: {context_str}. Your task now is to give a question about "
            f"the topic: {topic} that combines your knowledge and his/her experiences."
        )

        return self.agent1.inference(prompt)

    def received_message(self):
        # Mock implementation for demonstration purposes
        return "This is a mock received message."

    use_case()
