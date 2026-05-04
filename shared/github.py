import os
import subprocess
from contextlib import contextmanager

from githubkit import GitHub
from githubkit.auth import TokenAuthStrategy

USERNAME = "gx8z"


def _get_active_user() -> str:
    result = subprocess.run(
        ["gh", "api", "/user", "--jq", ".login"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _switch_user(username: str) -> None:
    subprocess.run(["gh", "auth", "switch", "--user", username], check=True)


def _get_gh_token() -> str:
    result = subprocess.run(
        ["gh", "auth", "token"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


@contextmanager
def github_client():
    """
    Yields an authenticated GitHub client.

    - In CI (GH_TOKEN present): uses the env var directly.
    - Locally: uses `gh auth token`. If the active gh user is not
      USERNAME, switches to it first and restores the previous
      user on exit.
    """
    token = os.environ.get("GH_TOKEN")

    if token:
        yield GitHub(TokenAuthStrategy(token))
        return

    active_user = _get_active_user()
    needs_switch = active_user != USERNAME

    try:
        if needs_switch:
            _switch_user(USERNAME)
        token = _get_gh_token()
        yield GitHub(TokenAuthStrategy(token))
    finally:
        if needs_switch:
            _switch_user(active_user)
