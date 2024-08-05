import json
import openai
import time

class ChatAgent:
    def __init__(self, name, resume):
        self.name = name
        self.resume = resume
        self.knowledge = self.extract_knowledge(resume)

    def extract_knowledge(self, resume):
        return resume  # Directly return the resume assuming it's already a dictionary

    def generate_response(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content']

    def chat(self, other_agent):
        common_projects = set(self.knowledge['projects']) & set(other_agent.knowledge['projects'])
        common_education = set(self.knowledge['education']) & set(other_agent.knowledge['education'])
        chat_history = []
        for _ in range(10):  # 10 conversations
            prompt1 = f"{self.name}, discuss your background based on the OCR text."
            response1 = self.generate_response(prompt1)
            chat_history.append(f'{self.name}: {response1}')
            time.sleep(1)  # Wait for 1 second

            prompt2 = f"{other_agent.name}, respond to the previous message."
            response2 = other_agent.generate_response(prompt2)
            chat_history.append(f'{other_agent.name}: {response2}')
            time.sleep(1)  # Wait for 1 second

        if common_projects:
            chat_history.append(f'{self.name}: We have worked on common projects: {", ".join(common_projects)}')
        if common_education:
            chat_history.append(f'{self.name}: We share a similar educational background: {", ".join(common_education)}')

        return chat_history


def create_agents(resume1, resume2):
    agent1 = ChatAgent('Agent 1', resume1)
    agent2 = ChatAgent('Agent 2', resume2)
    return agent1, agent2
