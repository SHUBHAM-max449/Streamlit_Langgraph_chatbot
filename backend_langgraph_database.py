from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

load_dotenv()
model=ChatOpenAI()
graph=StateGraph(ChatState)
conn = sqlite3.connect(database='chatbot.db',check_same_thread=False)
checkpointer=SqliteSaver(conn)

def chat_node(state:ChatState):
    last_message= state['messages'][-1]
    response=model.invoke(state['messages'])
    return {'messages':[response]}


def retrieve_all_threads():
    all_threads=set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)



graph.add_node("Chat_node", chat_node)

graph.add_edge(START,'Chat_node')
graph.add_edge('Chat_node',END)

workflow=graph.compile(checkpointer=checkpointer)
