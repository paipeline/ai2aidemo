# AI-to-AI Conversation System

## Overview

This program facilitates AI-to-AI conversations based on user-uploaded resumes. The main components of the system are:

- **Agent**: Represents an individual entity capable of engaging in conversations, processing resume information, and generating responses based on its knowledge.
- **Message**: Handles the generation of questions, responses, and greetings based on the conversation topic and history.
- **Flow**: Manages the conversation flow, including the conditions to change the topic or continue with the conversation.

## Components

### Agent

The `Agent` class is responsible for:

- Initializing with a resume and extracting relevant knowledge.
- Generating responses based on prompts.
- Updating its knowledge during the conversation.

**File**: `ai2aidemo/core/agent.py`

### Message

The `Message` class and its subclasses (`Question`, `Response`, `Greeting`) are responsible for:

- Generating messages (questions, responses, greetings) based on the conversation topic and history.
- Analyzing resumes and conversation history to create context-aware messages.

**File**: `ai2aidemo/core/message.py`

### Flow

The `Flow` class is responsible for:

- Managing the conversation flow between two agents.
- Deciding whether to explore new topics or exploit current ones based on the conversation history.
- Logging the conversation and its sequence.

**File**: `ai2aidemo/core/flow.py`

### Topics

The `Topics` class generates likely topics of conversation based on the knowledge and experience of two agents.

**File**: `ai2aidemo/core/topics.py`

## Usage

1. **Initialize Agents**: Create `Agent` instances with user-uploaded resumes.
2. **Generate Topics**: Use the `Topics` class to generate conversation topics.
3. **Start Conversation**: Use the `Flow` class to manage the conversation between the agents, utilizing the `Message` subclasses to generate questions, responses, and greetings.

## Example

Here is an example of how to use the system:

```python
from ai2aidemo.core.agent import Agent
from ai2aidemo.core.flow import Flow
from ai2aidemo.core.topics import Topics
from ai2aidemo.core.message import Greeting, Question, Response
from ai2aidemo.utils.pick_strategy import prob_based_pick

# Example resumes
resume1 = {
    "name": "Pai Eng",
    "education": {"degree": "Bachelor of Science", "major": "Computer Science", "university": "University of Barcelona"},
    "experience": "Software Engineer with 5 years of experience in AI and ML projects.",
    "skills": ["Python", "Machine Learning", "Deep Learning", "Data Science"],
    "projects": ["Developed an AI-based recommendation system for e-commerce platforms.", "Led a team in the creation of a machine learning model for predictive analytics in finance."],
    "others": ["Certified AI Professional", "Published research papers"]
}

resume2 = {
    "name": "Chong Chen",
    "education": [
        {"degree": "Bachelor of Science", "major": "Computer Sciences", "university": "University of Wisconsin-Madison", "gpa": "4.00/4.00", "location": "Madison, WI", "dates": "Aug. 2023 – Dec. 2024"},
        {"degree": "Bachelor of Science", "major": "Computer Engineering", "university": "The Ohio State University", "gpa": "3.74/4.00", "location": "Columbus, OH", "dates": "Aug. 2021 – May 2023"}
    ],
    "experience": [
        {"title": "Software Developer Intern", "company": "Shanghai MaiMiao Internet Ltd.", "location": "Remote", "dates": "May 2024 - Present", "responsibilities": ["Designed and developed a scalable, full-stack mobile app with React Native + Expo and Spring Boot + Java microservices, enhancing UX and business operations.", "Implemented efficient RESTful APIs and a flexible message service interface, optimizing system performance by 30% and enabling integration with various backends.", "Set up a CI/CD pipeline automating builds, tests, and deployments, reducing manual efforts by 80% and accelerating releases by 50%, ensuring code quality.", "Conducted code reviews, maintained documentation, and mentored junior developers, promoting best practices and collaboration."]},
        "Worked as a freelance developer, building various applications for clients."
    ],
    "skills": "Proficient in Python, Java, and C#",
    "others": "Additional information not structured"
}

# Initialize agents
agent1 = Agent(resume1, userID="123-456-7890")
agent2 = Agent(resume2, userID="098-765-4321")

# Generate topics
topics_generator = Topics(agent1_knowledge=agent1.enhanced_resume, agent2_knowledge=agent2.enhanced_resume)
topic = prob_based_pick(topics_generator.generate_conversation_topics())

# Start conversation flow
flow = Flow(agent1=agent1, agent2=agent2)
flow.iter()

# Print conversation history
print(flow.conversation_history)
```

## Logging

The system uses logging to record the conversation flow and important events. Logs are saved in `info.log` and `debug.log`.

## Future Work

- Implement learning mechanisms for the `__CONDITION__` function to determine when to change topics and how much more information to add.
- Enhance the scoring system for conversation quality and context relevance.
