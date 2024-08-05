import json
import logging
from openai import OpenAI
import time
client = OpenAI()
# Configure logging
logging.basicConfig(filename='agent_conversations.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class ChatAgent:
    def __init__(self, name, resume):
        self.name = name
        self.resume = resume
        self.knowledge = self.extract_knowledge(resume)

    def extract_knowledge(self, resume):
        return resume  # Directly return the resume assuming it's already a dictionary

    def generate_response(self, prompt):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for networking conversations."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message

    def chat(self, other_agent):
        text1 = self.knowledge['original_text']
        text2 = other_agent.knowledge['original_text']
        chat_history = []
        for _ in range(5):  # 5 conversations
            prompt1 = f"{self.name}, based on the following text, let's discuss our professional backgrounds and explore networking opportunities:\n{text1}"
            response1 = self.generate_response(prompt1)
            chat_history.append(f'{self.name}: {response1}')
            logging.info(f'{self.name}: {response1}')
            prompt2 = f"{other_agent.name}, based on the following text, how do you relate to the previous message and what networking opportunities do you see?\n{text2}"
            response2 = other_agent.generate_response(prompt2)
            chat_history.append(f'{other_agent.name}: {response2}')
            logging.info(f'{other_agent.name}: {response2}')
            time.sleep(1)  # Wait for 1 second

            prompt2 = f"{other_agent.name}, how do you relate to the previous message and what networking opportunities do you see?"
            response2 = other_agent.generate_response(prompt2)
            chat_history.append(f'{other_agent.name}: {response2}')
            time.sleep(1)  # Wait for 1 second


        for line in chat_history:
            yield line


def create_agents(resume1, resume2):
    agent1 = ChatAgent('Agent 1', resume1)
    agent2 = ChatAgent('Agent 2', resume2)
    return agent1, agent2
