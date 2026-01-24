from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

load_dotenv()
model=ChatOpenAI()
graph=StateGraph(ChatState)
checkpointer=MemorySaver()

def chat_node(state:ChatState):
    last_message= state['messages'][-1]
    response=model.invoke(state['messages'])
    return {'messages':[response]}


graph.add_node("Chat_node", chat_node)

graph.add_edge(START,'Chat_node')
graph.add_edge('Chat_node',END)

workflow=graph.compile(checkpointer=checkpointer)
