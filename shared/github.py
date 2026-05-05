import os
import subprocess
from typing import Literal, overload

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


class GitHubRepo:
    @overload
    def __init__(self, owner_or_full: str): ...

    @overload
    def __init__(self, owner_or_full: str, repo: str): ...

    def __init__(self, owner_or_full: str, repo: str | None = None):
        if repo is None:
            self.owner, self.repo = owner_or_full.split("/")
        else:
            self.owner = owner_or_full
            self.repo = repo

    @overload
    def get_release_asset_url(
        self,
        latest: Literal[True],
        tag: None = None,
        asset_name_includes: str | None = None,
        asset_name_endswith: str | None = None,
    ) -> str: ...

    @overload
    def get_release_asset_url(
        self,
        latest: Literal[False] | None = None,
        tag: str = ...,
        asset_name_includes: str | None = None,
        asset_name_endswith: str | None = None,
    ) -> str: ...

    def get_release_asset_url(
        self,
        latest: bool | None = False,
        tag: str | None = None,
        asset_name_includes: str | None = None,
        asset_name_endswith: str | None = None,
    ) -> str:
        release = None
        if latest:
            release = github_client.rest.repos.get_latest_release(
                owner=self.owner, repo=self.repo
            )
        elif tag:
            release = github_client.rest.repos.get_release_by_tag(
                owner=self.owner, repo=self.repo, tag=tag
            )

        if release:
            assets = release.parsed_data.assets
            if asset_name_includes:
                for asset in assets:
                    if asset_name_includes in asset.name:
                        return asset.browser_download_url
            if asset_name_endswith:
                for asset in assets:
                    if asset.name.endswith(asset_name_endswith):
                        return asset.browser_download_url
            return assets[0].browser_download_url
        else:
            raise Exception("No release found")
