import streamlit as st
from ai2aidemo.core.chat_agents import create_agents
from ai2aidemo.core.utils import load_resume, parse_pdf

st.title('Resume Chat Between LLM Agents')

# File uploader for resumes
resume_file1 = st.file_uploader('Upload Resume for Agent 1', type=['pdf'])
resume_file2 = st.file_uploader('Upload Resume for Agent 2', type=['pdf'])

if resume_file1 and resume_file2:
    st.write("Resume 1 type:", type(resume_file1))
    st.write("Resume 2 type:", type(resume_file2))

# Add a submit button
if st.button('Start Chat'):
    if resume_file1 and resume_file2:
        resume1 = parse_pdf(resume_file1)
        resume2 = parse_pdf(resume_file2)
        agent1, agent2 = create_agents(resume1, resume2)
        chat_history = []  # Initialize chat history list
        for line in agent1.chat(agent2):
            chat_history.append(line)  # Append each line to chat history

        # Display chat history in a chat-like format
        for message in chat_history:
            if message.startswith('Agent 1:'):
                st.markdown(f"<div style='text-align: left; background-color: #e1ffc7; padding: 10px; border-radius: 10px; margin: 5px;'> {message} </div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: right; background-color: #d1e7ff; padding: 10px; border-radius: 10px; margin: 5px;'> {message} </div>", unsafe_allow_html=True)
        for line in chat_history:
            st.text(line)
    else:
        st.warning('Please upload both resumes to start the chat.')
