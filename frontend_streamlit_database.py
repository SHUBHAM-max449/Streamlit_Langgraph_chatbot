import streamlit as st
from backend_langgraph_tools import workflow, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage
import uuid
from backend_langgraph import model

# +++++++++++++++++++++++++++++++++++++++ utility function +++++++++++++++++++++++++++++++++++++++

def generate_thread_id():
    thread_id= uuid.uuid4()
    return thread_id

def get_thread_name(thread_id):
    if thread_id in st.session_state['thread_name']:
        return st.session_state['thread_name'][thread_id]
    return str(thread_id)

def update_thread_name(thread_id,name):
    st.session_state['thread_name'][thread_id]=name

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def reset_messages():
    thread_id=generate_thread_id()
    st.session_state['thread_id']=thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history']=[]

def load_conversation(thread_id):
    state = workflow.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])


# +++++++++++++++++++++++++++++++++++++++= session_state ++++++++++++++++++++++++++++++

if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]

if 'thread_id' not in  st.session_state:
    st.session_state['thread_id']=generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=retrieve_all_threads()

if 'thread_name' not in st.session_state:
    st.session_state['thread_name']={}

add_thread(st.session_state['thread_id'])

# ++++++++++++++++++++++++++++++++++++++++ UI ++++++++++++++++++++++++++++++++++++++++

st.sidebar.title("Langgraph chatbot")

if st.sidebar.button("New Chat"):
    reset_messages()
    st.rerun()

st.sidebar.header("Conversation History")

for thread_id in st.session_state['chat_threads']:
    thread_name=get_thread_name(thread_id)
    if st.sidebar.button(thread_name, key=f"thread_{thread_id}"):
        st.session_state['thread_id']=thread_id
        messages=load_conversation(thread_id)
        temp_messages=[]

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            elif isinstance(msg, AIMessage):
                role='assistant'
            temp_messages.append({'role':role, 'content':msg.content})

        st.session_state['message_history']=temp_messages


# +++++++++++++++++++++++++++++++++++++++++++ Chatbot +++++++++++++++++++++++++++++++++

config={'configurable':{'thread_id':st.session_state['thread_id']},
        'metadata':{'thread_id':st.session_state['thread_id']},
        "run_name":"chat_run"}

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_message=st.chat_input()

if user_message:

    if len(st.session_state['message_history'])==0:
        thread_name=model.invoke(f"Create a concise, five-word chat title for the user message: {user_message}.ex: 'Calculation Related Query,' 'Medical Inquiry,' or another fitting category.").content
        update_thread_name(st.session_state['thread_id'],thread_name)
    st.session_state['message_history'].append({'role':'user','content':user_message})
    with st.chat_message('user'):
        st.text(user_message)

    with st.chat_message('assistant'):
        def ai_only_stream():
            for message_chunk,metadata in workflow.stream({'messages':[HumanMessage(content=user_message)]},config=config,stream_mode='messages'):
                if isinstance(message_chunk,AIMessage):
                    yield message_chunk.content
        ai_message=st.write_stream(ai_only_stream())
    st.session_state['message_history'].append({'role':'assistant','content':ai_message})
        
            

        