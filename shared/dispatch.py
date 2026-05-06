from shared.config import workspace_repo
from shared.github import github_client


def dispatch_json():
    github_client.rest.actions.create_workflow_dispatch(
        owner=workspace_repo.owner,
        repo=workspace_repo.repo,
        workflow_id="json.yml",
        ref="main",
    )
