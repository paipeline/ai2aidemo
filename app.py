import streamlit as st
from ai2aidemo.core.flow import Flow
from ai2aidemo.core.agent import Agent
from ai2aidemo.core.utils import load_resume, parse_pdf
from dotenv import load_dotenv
import time
import logging
load_dotenv()

st.set_page_config(page_title="AI Agents Chat", layout="wide")
st.title('AI Agents Networking Chat')

# Add description
st.markdown("""
This app demonstrates two AI agents having a professional networking conversation based on their resumes.
Upload two resumes and watch them engage in a natural dialogue!
""")

# Create two columns for resume uploads
col1, col2 = st.columns(2)

with col1:
    st.subheader("First Agent's Resume")
    resume_file1 = st.file_uploader('Upload Resume for Agent 1', type=['pdf'])

with col2:
    st.subheader("Second Agent's Resume")
    resume_file2 = st.file_uploader('Upload Resume for Agent 2', type=['pdf'])

# Add a number input for conversation turns
st.sidebar.subheader("Conversation Settings")
num_turns = st.sidebar.number_input(
    "Number of conversation turns", 
    min_value=1,
    max_value=10,
    value=3,
    help="Set how many back-and-forth exchanges the agents will have"
)

if st.button('Start Conversation', disabled=not (resume_file1 and resume_file2)):
    if resume_file1 and resume_file2:
        try:
            with st.spinner('Processing resumes and initializing agents...'):
                # Create agents directly from PDF files
                try:
                    agent1 = Agent(resume_file1)
                    agent2 = Agent(resume_file2)
                except Exception as e:
                    st.error(f"Error processing resumes: {str(e)}")
                    logging.error(f"Resume processing error: {str(e)}", exc_info=True)
                    st.stop()
                
                # Display agents' names
                st.info(f"Starting conversation between **{agent1.name}** and **{agent2.name}**")
                
                # Initialize flow with user-defined turns
                flow = Flow(agent1=agent1, agent2=agent2, num_turns=num_turns)
                
                # Create a container for the chat
                chat_container = st.container()
                
                with chat_container:
                    st.subheader("Conversation")
                    
                    # Execute conversation flow
                    flow.iter()
                    
                    # Display messages in chat format
                    for message in flow.conversation_history:
                        # Extract name and content
                        name, content = message.split(": ", 1)
                        
                        # Set avatar and style based on agent
                        if name == agent1.name:
                            avatar = "👨‍💼"  # Professional person 1
                            with st.chat_message("user", avatar=avatar):
                                st.write(f"**{name}**")
                                st.write(content)
                        else:
                            avatar = "👩‍💼"  # Professional person 2
                            with st.chat_message("assistant", avatar=avatar):
                                st.write(f"**{name}**")
                                st.write(content)
                        
                        # Add slight delay for visual effect
                        time.sleep(0.5)
                        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logging.error(f"Error during conversation: {e}", exc_info=True)
    else:
        st.warning('Please upload both resumes to start the conversation.')
