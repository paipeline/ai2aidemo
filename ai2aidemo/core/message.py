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

    agent1: Agent
    agent2: Agent
    @abstractmethod
    def send_message(self,topic,context):
        pass
    
    @abstractmethod 
    def received_message(self):
        pass
from typing import List

class Question(Message):
    """_summary_

    Args:
        ABC (_type_): _description_
    """
    
    def send_message(self, topic: str, context: List[str]):
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

    @staticmethod
    def use_case():
        # Mock implementation of Agent for demonstration purposes
        class MockAgent2(Agent):
            def __init__(self, name):
                self.name = name

            def inference(self, prompt):
                return f"Mock response to: {prompt}"

        # Create instances of MockAgent2
        agent1 = MockAgent2(name="Agent1")
        agent2 = MockAgent2(name="Agent")

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

        # Use the send_message method to generate a question
        generated_question = question.send_message(topic=topic, context=context)

        # Print the generated question
        print(generated_question)
    
    
if __name__ == "__main__":
    Question.use_case()
