## This frontend is without the streaming on the streamlit
import streamlit as st
import os
import base64, os, streamlit as st
from backend_gitlab import workflow, retrieve_all_threads
from backend_gitlab import workflow
from langchain_core.messages import HumanMessage
import uuid

# **************************************** utility functions *************************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = workflow.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])


# **************************************** Session Setup ******************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

# **************************************** Sidebar UI *********************************

st.sidebar.title('Gitter Convo')

if st.sidebar.button('New Convo'):
    reset_chat()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages

add_thread(st.session_state['thread_id'])

# **************************************** Main UI *********************************

png_path = os.path.join(os.path.dirname(__file__), "gitlab_logo.png")

with open(png_path, "rb") as f: 
    data = f.read()

b64 = base64.b64encode(data).decode()

st.markdown(
    f"""
    <div style="display:flex; align-items:center; justify-content:center; margin-bottom:1rem;">
        <img src="data:image/png;base64,{b64}" style="width:24px; height:24px; margin-right:8px;" />
        <span style="font-weight:600; font-size:1.25rem;">Gitter</span>
    </div>
    """,
    unsafe_allow_html=True
)

for message in st.session_state["message_history"]:
    with st.chat_message(message['role']):
       st.markdown(message['content'], unsafe_allow_html=True)

user_input = st.chat_input("Type your query here:")

if user_input:
    st.session_state['message_history'].append({'role':"user","content":user_input})
    with st.chat_message("user"):
        st.markdown(
        user_input,
    unsafe_allow_html=True
    )
    
    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {
            "thread_id": st.session_state["thread_id"]
        },
        "run_name": "chat_turn",
    }
    
    response=workflow.invoke({"messages":user_input}, config=CONFIG)
    ai_message=response['messages'][-1].content
    st.session_state['message_history'].append({'role':"assistant","content":ai_message})
    with st.chat_message("assistant",avatar="https://api.dicebear.com/7.x/bottts/svg?seed=AI"):
        #st.text(ai_message)   
        st.markdown(
        ai_message,
    unsafe_allow_html=True
)  