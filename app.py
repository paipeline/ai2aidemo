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
                try:
                    agent1 = Agent(resume_file1)
                    agent2 = Agent(resume_file2)
                except Exception as e:
                    st.error(f"Error processing resumes: {str(e)}")
                    logging.error(f"Resume processing error: {str(e)}", exc_info=True)
                    st.stop()
                
                # 添加CSS样式
                st.markdown("""
                <style>
                    .chat-container {
                        padding: 20px;
                        border-radius: 10px;
                        background-color: #f5f5f5;
                        margin: 10px 0;
                    }
                    .message-container {
                        display: flex;
                        margin: 10px 0;
                        align-items: flex-start;
                    }
                    .message-bubble {
                        padding: 12px 15px;
                        border-radius: 15px;
                        max-width: 80%;
                        margin: 5px;
                        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                    }
                    .message-left {
                        background-color: #e3f2fd;
                        margin-right: auto;
                        border-bottom-left-radius: 5px;
                    }
                    .message-right {
                        background-color: #f0fdf4;
                        margin-left: auto;
                        border-bottom-right-radius: 5px;
                    }
                    .avatar {
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        margin: 0 10px;
                    }
                    .name {
                        font-size: 0.8em;
                        color: #666;
                        margin-bottom: 5px;
                    }
                    .content {
                        font-size: 1em;
                        color: #333;
                        line-height: 1.4;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                # 显示代理名称
                st.info(f"Starting conversation between {agent1.name} and {agent2.name}")
                
                # 初始化对话流程
                flow = Flow(agent1=agent1, agent2=agent2, num_turns=num_turns)
                flow.iter()
                
                # 创建聊天容器
                with st.container():
                    for message in flow.conversation_history:
                        name, content = message.split(": ", 1)
                        
                        # 为每个代理设置不同的机器人图标和颜色
                        if name == agent1.name:
                            st.markdown(f"""
                            <div class="message-container">
                                <img src="https://api.dicebear.com/7.x/bottts/svg?seed=agent1" class="avatar">
                                <div class="message-bubble message-left">
                                    <div class="name">🤖 {name}</div>
                                    <div class="content">{content}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="message-container" style="flex-direction: row-reverse;">
                                <img src="https://api.dicebear.com/7.x/bottts/svg?seed=agent2" class="avatar">
                                <div class="message-bubble message-right">
                                    <div class="name" style="text-align: right;">🤖 {name}</div>
                                    <div class="content">{content}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # 添加消息动画延迟
                        time.sleep(0.5)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logging.error(f"Error during conversation: {e}", exc_info=True)
    else:
        st.warning('Please upload both resumes to start the conversation.')
