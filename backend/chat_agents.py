import json
import logging
from openai import OpenAI
import time
client = OpenAI()
# Configure logging
logging.basicConfig(filename='agent_conversations.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

class ChatAgent:
    def __init__(self, name, resume):
        self.conversation_history = []  # Initialize conversation history
        self.name = name
        self.resume = resume
        self.knowledge = self.extract_knowledge(resume)

    def get_name(self):
        return self.name  # Return the agent's name

    def extract_knowledge(self, resume):
        return resume  # Directly return the resume assuming it's already a dictionary

    def generate_response(self, prompt):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for networking conversations. here is your personal background"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def chat(self, other_agent):
        text1 = self.knowledge  # Use the raw text directly
        text2 = other_agent.knowledge  # Use the raw text directly
        chat_history = []
        for _ in range(5):  # Run for 10 exchanges
            prompt1 = f"{self.name}, based on the following text, let's discuss our professional backgrounds and explore networking opportunities:\n{text1}"
            response1 = self.generate_response(prompt1)
            chat_history.append(f'{self.name}: {response1}')
            self.conversation_history.append(f'{self.name}: {response1}')  # Record the conversation
            logging.info(f'{self.name}: {response1}')
            
            prompt2 = f"{other_agent.name}, based on the following text, how do you relate to the previous message and what networking opportunities do you see?\n{text2}"  # First response
            response2 = other_agent.generate_response(prompt2)
            chat_history.append(f'{other_agent.name}: {response2}')
            self.conversation_history.append(f'{other_agent.name}: {response2}')  # Record the conversation
            logging.info(f'{other_agent.name}: {response2}')
            time.sleep(1)  # Wait for 1 second

            prompt2 = f"{other_agent.name}, how do you relate to the previous message and what networking opportunities do you see?"  # Second response
            response2 = other_agent.generate_response(prompt2)
            chat_history.append(f'{other_agent.name}: {response2}')
            time.sleep(1)  # Wait for 1 second


        for line in chat_history:
            yield line


def create_agents(resume1, resume2):
    agent1 = ChatAgent('Agent 1', resume1)
    agent2 = ChatAgent('Agent 2', resume2)
    return agent1, agent2
