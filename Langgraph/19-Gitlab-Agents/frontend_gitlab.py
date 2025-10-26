## This frontend is without the streaming on the streamlit
import streamlit as st
import backend_gitlab
import os
import base64, os, streamlit as st

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

CONFIG= {"configurable":{"thread_id":"123"}}

if "message_history" not in st.session_state:
    st.session_state["message_history"]=[]

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

    response=backend_gitlab.workflow.invoke({"messages":user_input}, config=CONFIG)
    ai_message=response['messages'][-1].content
    st.session_state['message_history'].append({'role':"assistant","content":ai_message})
    with st.chat_message("assistant"):
        #st.text(ai_message)   
        st.markdown(
        ai_message,
    unsafe_allow_html=True
)  