from agent2 import Agent2
from abs import abs
from abc import ABC, abstractmethod


@
class Message(abs, ABC):
    """
    It takes three parameters: agent1 resumes, agent2 resumes, context, topics
    """
    def __init__(self, agent1,agent2, context, topics):
        pass 
    @abstractmethod
    def send_message(self):
        pass
    
