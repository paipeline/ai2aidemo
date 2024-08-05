import json

class ChatAgent:
    def __init__(self, name, resume):
        self.name = name
        self.resume = resume
        self.knowledge = self.extract_knowledge(resume)

    def extract_knowledge(self, resume):
        return resume  # Directly return the resume assuming it's already a dictionary

    def chat(self, other_agent):
        common_projects = set(self.knowledge['projects']) & set(other_agent.knowledge['projects'])
        common_education = set(self.knowledge['education']) & set(other_agent.knowledge['education'])
        chat_history = []

        if common_projects:
            chat_history.append(f'{self.name}: We have worked on common projects: {common_projects}')
        if common_education:
            chat_history.append(f'{self.name}: We share a similar educational background: {common_education}')

        return chat_history


def create_agents(resume1, resume2):
    agent1 = ChatAgent('Agent 1', resume1)
    agent2 = ChatAgent('Agent 2', resume2)
    return agent1, agent2
