## This frontend is without the streaming on the streamlit
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

    response=backend_chatbot.workflow.invoke({"messages":user_input}, config=CONFIG)
    ai_message=response['messages'][-1].content
    st.session_state['message_history'].append({'role':"assistant","content":ai_message})
    with st.chat_message("assistant"):
        st.text(ai_message)
        