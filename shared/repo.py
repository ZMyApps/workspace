import requests
from debian import debian_support

from shared.env import worker_base_url_with_auth


def parse_version(version: str):
    return debian_support.Version(version.replace("_", ""))


class SideloadRepo:
    def __init__(self, url: str):
        self.url = url

    def fetch(self):
        response = requests.get(self.url)
        repo_json = response.json()
        self.apps = repo_json["apps"]

    def filter_apps(
        self, name: str | None = None, bundle_identifier: str | None = None
    ):
        if name:
            return [app for app in self.apps if app["name"] == name]
        elif bundle_identifier:
            return [
                app for app in self.apps if app["bundleIdentifier"] == bundle_identifier
            ]

    def get_latest_app(
        self, name: str | None = None, bundle_identifier: str | None = None
    ):
        filtered_list = self.filter_apps(name=name, bundle_identifier=bundle_identifier)
        if filtered_list:
            sorted_list = sorted(
                filtered_list,
                key=lambda p: parse_version(p["version"]),
            )
            return sorted_list[-1]

    def get_app(
        self,
        version: str,
        name: str | None = None,
        bundle_identifier: str | None = None,
    ):
        filtered_list = self.filter_apps(name=name, bundle_identifier=bundle_identifier)
        if filtered_list:
            for app in filtered_list:
                if app["version"] == version:
                    return app


decrypted_repo = SideloadRepo(f"{worker_base_url_with_auth}/decrypted.json")
decrypted_latest_repo = SideloadRepo(
    f"{worker_base_url_with_auth}/decryptedlatest.json"
)
tweaked_repo = SideloadRepo(f"{worker_base_url_with_auth}/tweaked.json")
tweaked_latest_repo = SideloadRepo(f"{worker_base_url_with_auth}/tweakedlatest.json")
