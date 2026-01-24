from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import requests

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

load_dotenv()
model=ChatOpenAI()
graph=StateGraph(ChatState)
conn = sqlite3.connect(database='chatbot.db',check_same_thread=False)
checkpointer=SqliteSaver(conn=conn)

# Tool
search_tool=DuckDuckGoSearchRun(region='us-en')

@tool
def calculator(first_num:float,second_num:float,operation:str)->dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol:str)->dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=S4PQ9CYIFLUSD9H5"
    r=requests.get(url)
    return r.json()

tools=[search_tool,calculator,get_stock_price]

model_with_tool=model.bind_tools(tools)




def chat_node(state:ChatState):
    last_message= state['messages'][-1]
    response=model_with_tool.invoke(state['messages'])
    return {'messages':[response]}

tool_node=ToolNode(tools)

def retrieve_all_threads():
    all_threads=set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)


graph.add_node("Chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START,'Chat_node')
graph.add_conditional_edges("Chat_node",tools_condition)
graph.add_edge("tools","Chat_node")

workflow=graph.compile(checkpointer=checkpointer)
