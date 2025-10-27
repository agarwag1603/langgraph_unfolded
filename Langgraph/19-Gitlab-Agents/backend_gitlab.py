from typing import TypedDict, Annotated,Optional
from langgraph.graph import START,END,StateGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
import os
import requests
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

LANGCHAIN_PROJECT="Langgraph-Gitlab-Projects"

GITLAB_URL= os.environ["GITLAB_URL"]
# PROJECT_ID = os.getenv("PROJECT_ID")
TOKEN = os.getenv("GITLAB_PAT")

headers = {"PRIVATE-TOKEN": TOKEN}

gpt_llm= ChatOpenAI(model="gpt-4o-mini")
class ToolCaller(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    current_project_id: Optional[str] 
    
@tool
def fetch_gitlab_issues():
    """
    Tool to fetch all the open and closed issues in the gitlab.
    """
    project_id = PROJECT_ID
    headers = {"PRIVATE-TOKEN": TOKEN}
    url = f"{GITLAB_URL}/{project_id}/issues"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        issues = response.json()
        return [{"iid": i["iid"], "title": i["title"], "state": i["state"],"description": i["description"], 
                 "web_url": i["web_url"], "created_at":i["created_at"],"closed_at":i["closed_at"],"closed_by":i["author"]["username"]} 
                 for i in issues]
    else:
        return [{"error": response.text}]
        
@tool
def close_gitlab_issue(issue_iid: str) -> dict:
    """
    Based on the issue ID, the function will help close the open tickets.
    """
    project_id = PROJECT_ID
    headers = {"PRIVATE-TOKEN": TOKEN}
    url = f"{GITLAB_URL}/{project_id}/issues/{issue_iid}"
    data = {"state_event": "close"}

    response = requests.put(url, headers=headers, data=data)

    if response.status_code == 200:
        return {"message": f"Issue #{issue_iid} closed successfully."}
    else:
        return {"error": response.text}

@tool
def add_comment_to_issue(issue_iid: str, comment: str):
    """Add a comment to a GitLab issue."""
    project_id = PROJECT_ID
    headers = {"PRIVATE-TOKEN": TOKEN}
    url = f"{GITLAB_URL}/{project_id}/issues/{issue_iid}/notes"
    data = {"body": comment}

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 201:
        return {"message": f"Comment added to issue #{issue_iid} successfully."}
    else:
        return {"error": response.text}
    
@tool
def fetch_all_projects():
    """Fetch all the projects from gitlab."""
    headers = {"PRIVATE-TOKEN": TOKEN}
    url = GITLAB_URL
    params = {
    "membership": True,
    "simple": True,
    "per_page": 100
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        projects = response.json()
        
        return [{"project_name": p["name"], "project_id": p["id"], } 
                 for p in projects]
    
    else:
        return [{"error": response.text}]
    
@tool
def set_project_id(project_id: str):
    """
    Set the project ID to use for subsequent GitLab operations.
    Call this tool when user wants to work with a specific project.
    """
    return {"status": "success", "message": f"Project ID set to: {project_id}", "project_id": project_id}

tools = [fetch_gitlab_issues,close_gitlab_issue,add_comment_to_issue,fetch_all_projects,set_project_id]

llm_with_tools= gpt_llm.bind_tools(tools)

def chat_node(state: ToolCaller) -> ToolCaller:
    """LLM node that handles chat + tool calls. 
    """
    result = llm_with_tools.invoke(state["messages"])
    return {"messages": [result]}

# tool_node= ToolNode(tools)

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


graph=StateGraph(ToolCaller)
graph.add_node("chat_node",chat_node)
graph.add_node("tools",tool_node_with_state)

graph.add_edge(START,"chat_node")
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge("tools","chat_node")

checkpoint=InMemorySaver()

workflow=graph.compile(checkpointer=checkpoint)
