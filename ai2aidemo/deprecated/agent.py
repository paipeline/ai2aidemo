from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from typing import List, Dict, Any
from typing import TypedDict, Literal

# Define the config
class GraphConfig(TypedDict):
    model_name: Literal["openai"]

class ChatState(BaseModel):
    messages: List[Dict[str, Any]]

# Define Agents
agent1 = create_react_agent(
    ChatOpenAI(model="gpt-4", temperature=0.7),
    tools=[],
    state_modifier=lambda state: [
        {"role": "system", "content": "You are Agent 1, a friendly AI assistant. You know your name and your role."},
        *state["messages"],
        {"role": "assistant", "content": "Agent 1 is friendly and helpful."},
        {"role": "assistant", "content": "Agent 2 is curious and inquisitive."}
    ],
)

agent2 = create_react_agent(
    ChatOpenAI(model="gpt-4", temperature=0.7),
    tools=[],
    state_modifier=lambda state: [
        {"role": "system", "content": "You are Agent 2, a curious AI assistant. You know your name and your role."},
        *state["messages"],
        {"role": "assistant", "content": "Agent 2 is curious and inquisitive."},
        {"role": "assistant", "content": "Agent 1 is friendly and helpful."}
    ],
)

# Define the graph with the Pydantic model
graph = StateGraph(ChatState, config_schema=GraphConfig)

# Add nodes to the graph
graph.add_node("agent1", agent1)
graph.add_node("agent2", agent2)

# Set the entry point directly to "agent1"
graph.set_entry_point("agent1")

# Add edges between the nodes
graph.add_edge("agent1", "agent2")
graph.add_edge("agent2", "agent1")

# Compile the graph
compiled_graph = graph.compile()

# Initialize the state
initial_state = {"messages": []}

# Run the chat for a specified number of iterations
iterations = 5
for _ in range(iterations):
    state = compiled_graph.invoke(initial_state)
    for message in state["messages"]:
        print(f"{message['role'].capitalize()}: {message['content']}")
    print("---")
    initial_state = state  # Update the state for the next iteration