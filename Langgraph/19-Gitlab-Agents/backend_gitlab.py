from typing import TypedDict, Annotated
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
gpt_llm= ChatOpenAI(model="gpt-4o-mini")
class ToolCaller(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

@tool
def fetch_gitlab_issues():
    """
    Tool to fetch all the open and closed issues in the gitlab.
    """

    GITLAB_URL = "https://gitlab.com/api/v4"
    PROJECT_ID = os.getenv("PROJECT_ID")
    TOKEN = os.getenv("GITLAB_PAT")

    headers = {"PRIVATE-TOKEN": TOKEN}
    url = f"{GITLAB_URL}/projects/{PROJECT_ID}/issues"

    #params = {"state": "opened"}
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
    GITLAB_URL = "https://gitlab.com/api/v4"
    PROJECT_ID = os.getenv("PROJECT_ID")
    TOKEN = os.getenv("GITLAB_PAT")

    headers = {"PRIVATE-TOKEN": TOKEN}
    url = f"{GITLAB_URL}/projects/{PROJECT_ID}/issues/{issue_iid}"
    data = {"state_event": "close"}

    response = requests.put(url, headers=headers, data=data)

    if response.status_code == 200:
        return {"message": f"Issue #{issue_iid} closed successfully."}
    else:
        return {"error": response.text}

@tool
def add_comment_to_issue(issue_iid: str, comment: str):
    """Add a comment to a GitLab issue."""
    GITLAB_URL = "https://gitlab.com/api/v4"
    PROJECT_ID = os.getenv("PROJECT_ID")
    TOKEN = os.getenv("GITLAB_PAT")

    headers = {"PRIVATE-TOKEN": TOKEN}
    url = f"{GITLAB_URL}/projects/{PROJECT_ID}/issues/{issue_iid}/notes"
    data = {"body": comment}

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 201:
        return {"message": f"Comment added to issue #{issue_iid} successfully."}
    else:
        return {"error": response.text}

tools = [fetch_gitlab_issues,close_gitlab_issue,add_comment_to_issue]

llm_with_tools= gpt_llm.bind_tools(tools)

def chat_node(state: ToolCaller) -> ToolCaller:
    """LLM node that handles chat + tool calls. 
    """
    result = llm_with_tools.invoke(state["messages"])
    return {"messages": [result]}

tool_node= ToolNode(tools)


graph=StateGraph(ToolCaller)
graph.add_node("chat_node",chat_node)
graph.add_node("tools",tool_node)

graph.add_edge(START,"chat_node")
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge("tools","chat_node")

checkpoint=InMemorySaver()

workflow=graph.compile(checkpointer=checkpoint)
