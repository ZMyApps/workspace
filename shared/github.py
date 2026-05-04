import os
import subprocess

from githubkit import GitHub
from githubkit.auth import TokenAuthStrategy

USERNAME = "gx8z"

_token = os.environ.get("GH_TOKEN")

if not _token:
    token_cmd = subprocess.run(
        ["gh", "auth", "token", "--user", USERNAME],
        capture_output=True,
        text=True,
        check=True,
    )
    _token = token_cmd.stdout.strip()

if not _token:
    raise Exception("No token")

github_client = GitHub(TokenAuthStrategy(_token))
