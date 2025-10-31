from langchain_core.tools import tool
import backend_gitlab
import requests

###Fetch all the projects on gitlab
@tool
def fetch_all_projects():
    """Fetch all the projects from gitlab. If there are many more projects- safely prompt user any 5 projects only."""
    headers = {"PRIVATE-TOKEN": backend_gitlab.TOKEN}
    url = backend_gitlab.GITLAB_URL
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