from langchain_core.tools import tool
import backend_gitlab
import requests

###Add gitlab lables
@tool
def add_labels_to_issue(issue_iid: str, labels: str):
    """
    Add new labels to a GitLab issue without removing existing ones.
    
    Args:
        issue_iid: The issue IID (internal ID) to update
        labels: Comma-separated string of labels to ADD (e.g., "bug,high-priority")
                This will ADD these labels to any existing labels.
    
    Example: add_labels_to_issue("42", "urgent,needs-review")
    """
    project_id = backend_gitlab.PROJECT_ID
    if not project_id:
        return {"error": "No project selected. Please set a project first."}
    
    headers = {"PRIVATE-TOKEN": backend_gitlab.TOKEN}
    
    # First, get current labels
    get_url = f"{backend_gitlab.GITLAB_URL}/{project_id}/issues/{issue_iid}"
    get_response = requests.get(get_url, headers=headers)
    
    if get_response.status_code != 200:
        return {"error": f"Failed to fetch current labels: {get_response.text}"}
    
    current_labels = get_response.json().get("labels", [])
    new_labels_list = [label.strip() for label in labels.split(",")]
    
    # Combine current and new labels (remove duplicates)
    combined_labels = list(set(current_labels + new_labels_list))
    combined_labels_str = ",".join(combined_labels)
    
    # Update with combined labels
    put_url = f"{backend_gitlab.GITLAB_URL}/{project_id}/issues/{issue_iid}"
    data = {"labels": combined_labels_str}
    
    response = requests.put(put_url, headers=headers, data=data)
    
    if response.status_code == 200:
        return {"message": f"Added labels to issue #{issue_iid}. Current labels: {combined_labels_str}"}
    else:
        return {"error": response.text}

###Remove gitlab lables
@tool
def remove_labels_from_issue(issue_iid: str, labels: str):
    """
    Remove specific labels from a GitLab issue.
    
    Args:
        issue_iid: The issue IID (internal ID) to update
        labels: Comma-separated string of labels to REMOVE (e.g., "bug,wontfix")
    
    Example: remove_labels_from_issue("42", "wontfix,duplicate")
    """
    project_id = backend_gitlab.PROJECT_ID
    if not project_id:
        return {"error": "No project selected. Please set a project first."}
    
    headers = {"PRIVATE-TOKEN": backend_gitlab.TOKEN}
    
    # First, get current labels
    get_url = f"{backend_gitlab.GITLAB_URL}/{project_id}/issues/{issue_iid}"
    get_response = requests.get(get_url, headers=headers)
    
    if get_response.status_code != 200:
        return {"error": f"Failed to fetch current labels: {get_response.text}"}
    
    current_labels = get_response.json().get("labels", [])
    labels_to_remove = [label.strip() for label in labels.split(",")]
    
    # Remove specified labels
    remaining_labels = [label for label in current_labels if label not in labels_to_remove]
    remaining_labels_str = ",".join(remaining_labels)
    
    # Update with remaining labels
    put_url = f"{backend_gitlab.GITLAB_URL}/{project_id}/issues/{issue_iid}"
    data = {"labels": remaining_labels_str}
    
    response = requests.put(put_url, headers=headers, data=data)
    
    if response.status_code == 200:
        return {"message": f"Removed labels from issue #{issue_iid}. Current labels: {remaining_labels_str}"}
    else:
        return {"error": response.text}

###Update gitlab lables
@tool
def update_issue_labels(issue_iid: str, labels: str):
    """
    Update or add labels to a GitLab issue.
    
    Args:
        issue_iid: The issue IID (internal ID) to update
        labels: Comma-separated string of labels to set (e.g., "bug,high-priority,backend")
                This will REPLACE all existing labels with the new ones.
    
    Example: update_issue_labels("42", "bug,urgent,needs-review")
    """
    project_id = backend_gitlab.PROJECT_ID
    if not project_id:
        return {"error": "No project selected. Please set a project first."}
    
    headers = {"PRIVATE-TOKEN": backend_gitlab.TOKEN}
    url = f"{backend_gitlab.GITLAB_URL}/{project_id}/issues/{issue_iid}"
    data = {"labels": labels}

    response = requests.put(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return {"message": f"Labels updated for issue #{issue_iid} to: {labels}"}
    else:
        return {"error": response.text}