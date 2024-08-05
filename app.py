import streamlit as st
from backend.chat_agents import create_agents
from backend.utils import load_resume

st.title('Resume Chat Between LLM Agents')

# File uploader for resumes
resume_file1 = st.file_uploader('Upload Resume for Agent 1', type=['json'])
resume_file2 = st.file_uploader('Upload Resume for Agent 2', type=['json'])

if resume_file1 and resume_file2:
    resume1 = load_resume(resume_file1)
    resume2 = load_resume(resume_file2)
    agent1, agent2 = create_agents(resume1, resume2)
    chat_history = agent1.chat(agent2)

    # Display chat history
    for line in chat_history:
        st.text(line)
else:
    st.warning('Please upload both resumes to see the chat.')
