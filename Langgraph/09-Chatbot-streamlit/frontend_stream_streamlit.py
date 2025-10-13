## This frontend is with the streaming on the streamlit

import streamlit as st
import backend_chatbot

st.title("Robochat")

CONFIG= {"configurable":{"thread_id":"123"}}

if "message_history" not in st.session_state:
    st.session_state["message_history"]=[]

for message in st.session_state["message_history"]:
    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input("Type your query here:")

if user_input:
    st.session_state['message_history'].append({'role':"user","content":user_input})
    with st.chat_message("user"):
        st.text(user_input)

    with st.chat_message("assistant"):
        ai_response=st.write_stream(
         message_chunk.content for message_chunk, metadata in backend_chatbot.workflow.stream({"messages":user_input}, config=CONFIG, stream_mode="messages")
        )

    st.session_state['message_history'].append({'role':"assistant","content":ai_response})
        