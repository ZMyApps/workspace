import os
import subprocess

from githubkit import GitHub
from githubkit.auth import ActionAuthStrategy, TokenAuthStrategy

USERNAME = "gx8z"


def get_github_client():
    if os.getenv("GITHUB_ACTIONS") == "true":
        _github = GitHub(ActionAuthStrategy())
    else:
        token_cmd = subprocess.run(
            ["gh", "auth", "token", "--user", USERNAME],
            capture_output=True,
            text=True,
            check=True,
        )
        token = token_cmd.stdout.strip()
        _github = GitHub(TokenAuthStrategy(token))
    return _github


github_client = get_github_client()
