## Backend for the chatbot-  same as ipynb file
from typing import TypedDict, Annotated,Literal
from langgraph.graph import START,END,StateGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


load_dotenv()
gpt_llm= ChatOpenAI(model="gpt-4o-mini")

class MessageClassifier(BaseModel):
    MessageClassifier: Literal["Physics","Maths","Chemistry"] = Field(description="This is a message classfier")
structured_llm=gpt_llm.with_structured_output(MessageClassifier)
class Chatbot(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]
    MessageClassifier: str


def message_classifier(state:Chatbot)->Chatbot:
   
    prompt=f"Based on the message provided by the user: \n {state['messages']}, classify the message."
   
    response=structured_llm.invoke(prompt)

    return {"MessageClassifier":response.MessageClassifier}
def physics_chatbot(state: Chatbot) -> Chatbot:
    
    prompt= f"You are an intelligent physics poet who always try to write rhyming poems based on the user input for the message: \n {state['messages']}."
    
    response = gpt_llm.invoke(prompt)
    
    return {'messages':[response]}

def math_chatbot(state: Chatbot) -> Chatbot:
   
    prompt= f"You are an intelligent math instructor who answers user's questions based on the user query along real life analogy: \n {state['messages']}."

    response = gpt_llm.invoke(prompt)

    return {'messages':[response]}
def chemistry_chatbot(state: Chatbot) -> Chatbot:
   
    prompt= f"You are an intelligent chemistry blog generator who answers user's questions by writing blogs in details: \n {state['messages']}."
    
    response = gpt_llm.invoke(prompt)

    return {'messages':[response]}
def messageclassifier_check(state: Chatbot) -> Literal["physics_chatbot","math_chatbot","chemistry_chatbot"]:
    if state['MessageClassifier']=="Physics":
        return "physics_chatbot"
    elif state['MessageClassifier']=="Maths":
        return "math_chatbot"
    else:
        return "chemistry_chatbot"


checkpoint=InMemorySaver()

graph=StateGraph(Chatbot)
graph.add_node("message_classifier",message_classifier)
graph.add_node("physics_chatbot",physics_chatbot)
graph.add_node("math_chatbot",math_chatbot)
graph.add_node("chemistry_chatbot",chemistry_chatbot)

graph.add_edge(START, "message_classifier")
graph.add_conditional_edges("message_classifier",messageclassifier_check)
graph.add_edge("physics_chatbot", END)
graph.add_edge("math_chatbot", END)
graph.add_edge("chemistry_chatbot", END)
workflow=graph.compile(checkpointer=checkpoint)