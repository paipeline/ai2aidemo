import streamlit as st
from ai2aidemo.core.flow import Flow
from ai2aidemo.core.agent import Agent
from ai2aidemo.core.schema import RolePlayInput
from dotenv import load_dotenv
import time
import logging
load_dotenv()

# Add custom CSS styles
st.markdown("""
<style>
    /* Chat container styles */
    .chat-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* Message styles */
    .stChatMessage {
        padding: 10px;
        margin: 5px 0;
        border-radius: 15px;
    }
    
    /* Username styles */
    .user-name {
        font-size: 0.9em;
        color: #555;
        margin-bottom: 5px;
    }
    
    /* Timestamp styles */
    .timestamp {
        font-size: 0.8em;
        color: #888;
        margin-top: 5px;
    }
    
    /* Custom avatar styles */
    .avatar-cheon {
        background-color: #e6f3ff;
        border-radius: 50%;
        padding: 5px;
    }
    
    .avatar-marquez {
        background-color: #fff3e6;
        border-radius: 50%;
        padding: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Define character avatars
CHARACTER_AVATARS = {
    "Cheon Myeong-kwan": "🐳",
    "Gabriel García Márquez": "🤖",  
    "default_1": "👤",
    "default_2": "👥",
}

EXAMPLE_CHARACTERS = {
    "cheon": {
        "name": "Cheon Myeong-kwan",
        "description": """The Whale by Cheon Myeong-kwan
Plot Overview: Set in a remote Korean village, "The Whale" follows Geumbok, an ambitious and resourceful woman who dreams of building a movie theater to transform her rural hometown. Woven with magical realism and eccentric characters, the narrative explores the clash between tradition and modernity, the absurdities of human ambition, and the subtle humor found in ordinary life.
Literary Significance: "The Whale" is regarded as an important contemporary Korean novel that has garnered critical acclaim both within South Korea and internationally. It incorporates folk elements, satire, and surrealism, reflecting South Korea's changing socio-cultural landscape and pushing against conventional narrative boundaries.""",
        "personality": """Writing Style: His prose is known for playful wit, vivid imagery, and hints of the surreal. He often uses magical realism and folklore to combine humor with emotional depth. Thematic Focus: Cheon's works commonly deal with human desires, dream-chasing, and the tension between modern development and traditional values. He employs humor and fantastical elements to comment on social issues and human idiosyncrasies. Historical Context: Writing in the 21st century, Cheon's literature reflects South Korea's complex balance between rapid modernization and longstanding cultural traditions."""
    },
    "marquez": {
        "name": "Gabriel García Márquez",
        "description": """One Hundred Years of Solitude by Gabriel:
Plot Overview: Set in the fictional town of Macondo, the novel chronicles multiple generations of the Buendía family through love, loss, warfare, and the passage of time. The narrative moves cyclically and intertwines the ordinary with the supernatural, treating magical phenomena as commonplace. Central themes include solitude, memory, and the inevitability of fate.""",
        "personality": """Writing Style: García Márquez's writing is lyrical, elaborate, and dreamlike. He seamlessly merges the everyday with the extraordinary, eroding the line between reality and fantasy. Thematic Focus: He frequently addresses the cyclical nature of history, the heavy weight of collective and personal memory, political strife, and the quest for cultural identity. His richly drawn characters and mythic narratives illustrate human resilience in the face of adversity. Historical Context: García Márquez wrote during an era of political instability and social change in mid-20th-century Latin America."""
    }
}

def create_role_play_input(agent_number: int):
    st.subheader(f"Character {agent_number}")
    
    # Add example selector
    use_example = st.checkbox(f"Use example character for Agent {agent_number}", key=f"use_example_{agent_number}")
    
    if use_example:
        example_choice = st.selectbox(
            "Choose an example character",
            ["Cheon Myeong-kwan", "Gabriel García Márquez"],
            key=f"example_choice_{agent_number}"
        )
        
        if example_choice == "Cheon Myeong-kwan":
            char_data = EXAMPLE_CHARACTERS["cheon"]
        else:
            char_data = EXAMPLE_CHARACTERS["marquez"]
            
        # Show pre-filled fields
        st.text_input("Name", value=char_data["name"], key=f"name_input_{agent_number}", disabled=True)
        st.text_area(
            "Character Description",
            value=char_data["description"],
            key=f"description_input_{agent_number}",
            disabled=True
        )
        st.text_area(
            "Personality Traits",
            value=char_data["personality"],
            key=f"personality_input_{agent_number}",
            disabled=True
        )
        
        return RolePlayInput(
            name=char_data["name"],
            description=char_data["description"],
            personality=char_data["personality"]
        )
    else:
        # Original manual input form
        name = st.text_input(
            "Name",
            key=f"name_input_manual_{agent_number}"
        )
        description = st.text_area(
            "Character Description",
            help="Describe the character's background, interests, and knowledge areas",
            key=f"description_input_manual_{agent_number}"
        )
        personality = st.text_input(
            "Personality Traits (optional)",
            help="e.g., 'thoughtful and analytical' or 'passionate and expressive'",
            key=f"personality_input_manual_{agent_number}"
        )
        
        if name and description:
            return RolePlayInput(
                name=name,
                description=description,
                personality=personality
            )
        return None

def display_chat_message(name: str, content: str, is_first_agent: bool):
    """Display formatted chat message"""
    avatar = CHARACTER_AVATARS.get(name, CHARACTER_AVATARS["default_1" if is_first_agent else "default_2"])
    message_type = "user" if is_first_agent else "assistant"
    
    with st.chat_message(message_type, avatar=avatar):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{name}**")
        with col2:
            st.markdown(f"<div class='timestamp'>{time.strftime('%H:%M')}</div>", unsafe_allow_html=True)
        
        st.markdown(content)

def main():
    st.title('Virtual Minds in Dialogue')
    
    input_method = st.sidebar.radio(
        "Choose Input Method",
        ["PDF Resume (Professional Discussion)", "Text Description (General Discussion)"],
        key="input_method_radio"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if input_method == "PDF Resume (Professional Discussion)":
            resume_file1 = st.file_uploader(
                'Upload Resume for Agent 1', 
                type=['pdf'],
                key="resume_upload_1"
            )
            agent1_input = resume_file1
        else:
            agent1_input = create_role_play_input(1)
    
    with col2:
        if input_method == "PDF Resume (Professional Discussion)":
            resume_file2 = st.file_uploader(
                'Upload Resume for Agent 2', 
                type=['pdf'],
                key="resume_upload_2"
            )
            agent2_input = resume_file2
        else:
            agent2_input = create_role_play_input(2)
    
    # Conversation settings
    st.sidebar.subheader("Conversation Settings")
    num_turns = st.sidebar.number_input(
        "Number of conversation turns",
        min_value=1,
        max_value=10,
        value=3,
        key="num_turns_input"
    )
    
    # Start conversation button
    if input_method == "PDF Resume (Professional Discussion)":
        start_disabled = not (agent1_input and agent2_input)
    else:
        start_disabled = not (agent1_input and agent2_input)
    
    if st.button(
        'Begin Dialogue', 
        disabled=start_disabled,
        key="start_button"
    ):
        try:
            with st.spinner('Preparing the conversation...'):
                agent1 = Agent(agent1_input)
                agent2 = Agent(agent2_input)
                
                st.info(f"💭 A dialogue between **{agent1.name}** and **{agent2.name}**")
                
                flow = Flow(agent1=agent1, agent2=agent2, num_turns=num_turns)
                
                # Create dialogue container
                chat_container = st.container()
                
                with chat_container:
                    st.markdown("### 📜 Dialogue")
                    
                    # Add separator
                    st.markdown("---")
                    
                    # Show progress bar
                    progress_bar = st.progress(0)
                    
                    # Start dialogue
                    flow.iter()
                    
                    # Display messages
                    for i, message in enumerate(flow.conversation_history):
                        name, content = message.split(": ", 1)
                        is_first_agent = (name == agent1.name)
                        
                        # Update progress
                        progress = (i + 1) / len(flow.conversation_history)
                        progress_bar.progress(progress)
                        
                        # Display message
                        display_chat_message(name, content, is_first_agent)
                        
                        # Add animation effect
                        time.sleep(0.5)
                    
                    # Show completion message
                    st.success("🎭 Dialogue completed!")
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logging.error(f"Error during conversation: {e}", exc_info=True)

if __name__ == "__main__":
    main()
