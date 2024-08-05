import streamlit as st
from backend.chat_agents import create_agents
from backend.utils import load_resume, parse_pdf

st.title('Resume Chat Between LLM Agents')

# File uploader for resumes
resume_file1 = st.file_uploader('Upload Resume for Agent 1', type=['pdf'])
resume_file2 = st.file_uploader('Upload Resume for Agent 2', type=['pdf'])

if resume_file1 and resume_file2:
    resume1 = parse_pdf(resume_file1)
    resume2 = parse_pdf(resume_file2)
    agent1, agent2 = create_agents(resume1, resume2)
    chat_history = agent1.chat(agent2)  # Create a generator for real-time updates
    for line in chat_history:
        st.text(line)  # Display each line as it is generated
        st.experimental_rerun()  # Rerun the app to show the latest conversation

    # Display chat history
    for line in chat_history:
        st.text(line)
else:
    st.warning('Please upload both resumes to see the chat.')
