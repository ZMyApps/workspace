from time import time

import requests
from debian import debian_support

from shared.config import all_apps
from shared.repo import decrypted_latest_repo, tweaked_latest_repo


def lookup_appstore(bundle_identifier: str):
    url = f"https://itunes.apple.com/lookup?bundleId={bundle_identifier}&cacheBusting={time()}"
    with requests.get(url, stream=True) as response:
        data = response.json()
        return (data["results"][0]["version"], data["results"][0]["trackViewUrl"])


def main():
    decrypted_latest_repo.fetch()
    tweaked_latest_repo.fetch()

    print(
        f"{'name':<14}",
        f"{'appstore':<9}",
        f"{'decrypted':<9}",
        f"{'': <2}",
        f"{'tweaked':<9}",
        f"{'': <2}",
        f"{'link'}",
    )
    print(
        "---------------------------------------------------------------------------------------------------"
    )

    for app in all_apps:
        bundle_identifier = app["bundle_identifier"]
        appstore_version, appstore_link = lookup_appstore(
            bundle_identifier=bundle_identifier
        )
        decrypted = decrypted_latest_repo.get_latest_app(
            bundle_identifier=bundle_identifier
        )
        decrypted_version = decrypted["version"] if decrypted is not None else ""
        tweaked = tweaked_latest_repo.get_latest_app(
            bundle_identifier=bundle_identifier
        )
        tweaked_version = (
            tweaked["version"].split("_")[0] if tweaked is not None else ""
        )
        decrypted_outdated = ""
        if appstore_version and decrypted_version and app["name"] not in ["Apollo"]:
            decrypted_outdated = (
                "✓"
                if debian_support.Version(appstore_version)
                > debian_support.Version(decrypted_version)
                else ""
            )
        tweaked_outdated = ""
        if appstore_version and tweaked_version and app["name"] not in ["Apollo"]:
            tweaked_outdated = (
                "✓"
                if debian_support.Version(appstore_version)
                > debian_support.Version(tweaked_version)
                else ""
            )

        print(
            f"{app['name']:<14}",
            f"{appstore_version:<9}",
            f"{decrypted_version:<9}",
            f"{decrypted_outdated: <2}",
            f"{tweaked_version:<9}",
            f"{tweaked_outdated: <2}",
            f"{appstore_link}",
        )


if __name__ == "__main__":
    main()
