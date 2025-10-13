## This frontend is with the streaming on the streamlit

import streamlit as st
import backend_chatbot
import uuid
from langchain_core.messages import HumanMessage, AIMessage

def generate_thread_id():
    thread_id=uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id=generate_thread_id()
    st.session_state["thread_id"]=thread_id
    add_thread(st.session_state["thread_id"])
    st.session_state["message_history"]=[]

def add_thread(thread_id):
    if thread_id not in st.session_state['chatbot_thread']:
        st.session_state['chatbot_thread'].append(thread_id)

def load_conversation(thread_id):
    return backend_chatbot.workflow.get_state(config={"configurable":{"thread_id":thread_id}}).values["messages"]

if "message_history" not in st.session_state:
    st.session_state["message_history"]=[]

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chatbot_thread" not in st.session_state:
    st.session_state["chatbot_thread"] = []

add_thread(st.session_state['thread_id'])



st.sidebar.title("🤖 Robochat")
if st.sidebar.button("New Conversation"):
    reset_chat()
st.sidebar.header("Past Conversation")

for thread_id in st.session_state["chatbot_thread"][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state["thread_id"]=thread_id
        messages=load_conversation(thread_id)

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages
    

for message in st.session_state["message_history"]:
    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input("Type your query here:")

if user_input:
    st.session_state['message_history'].append({'role':"user","content":user_input})
    with st.chat_message("user"):
        st.text(user_input)

    CONFIG= {"configurable":{"thread_id":st.session_state["thread_id"]}}

    with st.chat_message("assistant"):
        ai_response=st.write_stream(
         message_chunk.content for message_chunk, metadata in backend_chatbot.workflow.stream({"messages":user_input}, config=CONFIG, stream_mode="messages")
        )

    st.session_state['message_history'].append({'role':"assistant","content":ai_response})
        