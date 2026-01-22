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
    prompt=f"""
answer to the user query {state['messages']}
"""
    response=model.invoke(prompt).content
    return {'messages':[response]}


graph.add_node("Chot_node", chat_node)

graph.add_edge(START,'Chot_node')
graph.add_edge('Chot_node',END)

workflow=graph.compile(checkpointer=checkpointer)



