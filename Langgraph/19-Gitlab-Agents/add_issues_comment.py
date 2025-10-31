from langchain_core.tools import tool
import backend_gitlab
import requests


###Adding comments to the issues
@tool
def add_comment_to_issue(issue_iid: str, comment: str):
    """Add a comment to a GitLab issue.
    If user doesn't provide an issue_iid, prompt them to provide the issue_iid.
    """
    project_id = backend_gitlab.PROJECT_ID
    headers = {"PRIVATE-TOKEN": backend_gitlab.TOKEN}
    url = f"{backend_gitlab.GITLAB_URL}/{project_id}/issues/{issue_iid}/notes"
    data = {"body": comment}

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 201:
        return {"message": f"Comment added to issue #{issue_iid} successfully."}
    else:
        return {"error": response.text}