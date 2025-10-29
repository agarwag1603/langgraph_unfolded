from langchain_core.tools import tool
import backend_gitlab
import requests

@tool
def create_gitlab_issue(title: str, description: str , labels: str , assignee_id: str = ""):
    """
    Create a new issue in the currently active GitLab project.
    
    Args:
        title: The title of the issue (required)
        description: The description/body of the issue (required)
        labels: Comma-separated string of labels (required, e.g., "bug,high-priority")
        assignee_id: The user ID to assign the issue to (optional)
    
    If user does not give the all required field of title/description/labels, do not create issue. Prompt them to provide important information.
    
    Example: create_gitlab_issue("Fix login bug", "Users cannot login with special characters", "bug,urgent")
    """
    project_id = backend_gitlab.PROJECT_ID
    if not project_id:
        return {"error": "No project selected. Please set a project first using set_project_id."}
    
    headers = {"PRIVATE-TOKEN": backend_gitlab.TOKEN}
    url = f"{backend_gitlab.GITLAB_URL}/{project_id}/issues"
    
    data = {
        "title": title,
        "description": description,
    }
    
    if labels:
        data["labels"] = labels
    
    if assignee_id:
        data["assignee_ids"] = [assignee_id]
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 201:
        issue = response.json()
        return {
            "message": f"Issue created successfully!",
            "iid": issue["iid"],
            "title": issue["title"],
            "web_url": issue["web_url"],
            "state": issue["state"]
        }
    else:
        return {"error": response.text}