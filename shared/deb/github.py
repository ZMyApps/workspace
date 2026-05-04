from typing import Literal, overload

from shared.github import github_client


class GithubRepo:
    def __init__(self, owner: str, repo: str):
        self.owner = owner
        self.repo = repo

    @overload
    def get_release_asset_url(
        self,
        latest: Literal[True],
        tag: None = None,
        asset_name_includes: str | None = None,
    ) -> str: ...

    @overload
    def get_release_asset_url(
        self,
        latest: Literal[False] | None = None,
        tag: str = ...,
        asset_name_includes: str | None = None,
    ) -> str: ...

    def get_release_asset_url(
        self,
        latest: bool | None = False,
        tag: str | None = None,
        asset_name_includes: str | None = None,
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
            return assets[0].browser_download_url
        else:
            raise Exception("No release found")
