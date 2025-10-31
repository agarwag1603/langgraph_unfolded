from langchain_core.tools import tool
import backend_gitlab
import requests

###Closing the issues on gitlab
@tool
def close_gitlab_issue(issue_iid: str) -> dict:
    """
    Based on the issue ID, the function will help close the open tickets.
    If user doesn't provide an issue_iid, prompt them to provide the issue_iid.
    """
    project_id = backend_gitlab.PROJECT_ID
    headers = {"PRIVATE-TOKEN": backend_gitlab.TOKEN}
    url = f"{backend_gitlab.GITLAB_URL}/{project_id}/issues/{issue_iid}"
    data = {"state_event": "close"}

    response = requests.put(url, headers=headers, data=data)

    if response.status_code == 200:
        return {"message": f"Issue #{issue_iid} closed successfully."}
    else:
        return {"error": response.text}