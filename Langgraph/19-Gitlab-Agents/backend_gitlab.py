from typing import TypedDict, Annotated,Optional
from langgraph.graph import START,END,StateGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from fetch_gitlab_issues import fetch_gitlab_issues
from gitlab_labels import add_labels_to_issue, remove_labels_from_issue, update_issue_labels
from close_gitlab_issues import close_gitlab_issue
from add_issues_comment import add_comment_to_issue
from fetch_all_projects import fetch_all_projects
from create_issues_gitlab import create_gitlab_issue
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os

load_dotenv()

os.environ['LANGCHAIN_PROJECT']="Langgraph-Gitlab-Projects"

GITLAB_URL= os.environ["GITLAB_URL"]
# PROJECT_ID = os.getenv("PROJECT_ID")
TOKEN = os.getenv("GITLAB_PAT")

headers = {"PRIVATE-TOKEN": TOKEN}

gpt_llm= ChatOpenAI(model="gpt-4o-mini")
class ToolCaller(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    current_project_id: Optional[str] 
    
@tool
def set_project_id(project_id: str):
    """
    Set the project ID to use for subsequent GitLab operations.
    Call this tool when user wants to work with a specific project.
    """
    return {"status": "success", "message": f"Project ID set to: {project_id}", "project_id": project_id}


tools = [create_gitlab_issue,fetch_gitlab_issues,close_gitlab_issue,add_comment_to_issue,fetch_all_projects,set_project_id,
         update_issue_labels,add_labels_to_issue,remove_labels_from_issue]

llm_with_tools= gpt_llm.bind_tools(tools)

def chat_node(state: ToolCaller) -> ToolCaller:
    """LLM node that handles chat + tool calls. 
    """
    result = llm_with_tools.invoke(state["messages"])
    return {"messages": [result]}

def tool_node_with_state(state: ToolCaller):
    """Execute tools and update current_project_id if set_project_id was called."""
    result = ToolNode(tools).invoke(state)

    updated_project_id = state.get("current_project_id")
    for msg in result["messages"]:
        if hasattr(msg, "content") and "project_id" in str(msg.content):
            import json
            try:
                content = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                if isinstance(content, dict) and "project_id" in content:
                    updated_project_id = content["project_id"]
                    global PROJECT_ID
                    PROJECT_ID = updated_project_id
            except:
                pass
    
    return {"messages": result["messages"], "current_project_id": updated_project_id}

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# Checkpointer
Checkpointer= SqliteSaver(conn=conn)

graph=StateGraph(ToolCaller)
graph.add_node("chat_node",chat_node)
graph.add_node("tools",tool_node_with_state)

graph.add_edge(START,"chat_node")
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge("tools","chat_node")

# checkpoint=InMemorySaver()

workflow=graph.compile(checkpointer=Checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in Checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)