import streamlit as st
from backend_langgraph import workflow
from langchain_core.messages import HumanMessage


config={'configurable':{'thread_id':1}}

if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_message=st.chat_input()

if user_message:
    st.session_state['message_history'].append({'role':'user','content':user_message})
    with st.chat_message('user'):
        st.text(user_message)


    response=workflow.invoke({'messages':[HumanMessage(content=user_message)]}, config=config)
    ai_message=response['messages'][-1].content
    st.session_state['message_history'].append({'role':'assistant','content':ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)