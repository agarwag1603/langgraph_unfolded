from langchain_core.tools import tool
import backend_gitlab
import requests

###Fetch all the gitlab issues - opened/closed
@tool
def fetch_gitlab_issues():
    """
    Tool to fetch all the open and closed issues in a specific gitlab project.
    IMPORTANT: This requires a project to be set. If no project is currently set,
    you should first ask the user which project they want to check, or list all 
    projects using fetch_all_projects.
    """
    project_id = backend_gitlab.PROJECT_ID
    headers = {"PRIVATE-TOKEN": backend_gitlab.TOKEN}
    url = f"{backend_gitlab.GITLAB_URL}/{project_id}/issues"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        issues = response.json()
        return [{"iid": i["iid"], "title": i["title"], "state": i["state"],"description": i["description"], 
                 "web_url": i["web_url"], "created_at":i["created_at"],"closed_at":i["closed_at"],"closed_by":i["author"]["username"]} 
                 for i in issues]
    else:
        return [{"error": response.text}]