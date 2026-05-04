import json

from debian.debian_support import Version

from shared.config import get_app_config, ipa_archive_repo
from shared.github import GitHubRepo, github_client


def list_releases(github_repo: GitHubRepo):
    return github_client.rest.paginate(
        github_client.rest.repos.list_releases,
        owner=github_repo.owner,
        repo=github_repo.repo,
        per_page=100,
    )


def generate_decrypted():
    decrypted = []
    decrypted_latest = {}
    for release in list_releases(ipa_archive_repo):
        for asset in release.assets:
            asset_name_splitted = asset.name.removesuffix(".ipa").split("_")
            if len(asset_name_splitted) < 2 or len(asset_name_splitted) > 3:
                print(
                    "generate_decrypted -- abnormal len(asset_name_splitted) =",
                    len(asset_name_splitted),
                )
                continue
            app_name: str = asset_name_splitted[0]
            app_version: str = asset_name_splitted[1]
            app_config = get_app_config(name=app_name)
            if not app_config:
                print("generate_decrypted -- app_config for ", app_name, "not found")
                continue
            current_app_json = {
                "name": app_name,
                "bundleIdentifier": app_config["bundle_identifier"],
                "version": app_version,
                "localizedDescription": asset.name,
                "downloadURL": f"{worker_base_url}/download/{ipa_archive_repo.owner}/{ipa_archive_repo.repo}/{asset.id}/{asset.name}",
                "iconURL": f"{worker_base_url}/icon/{app_name}.jpg",
                "versionDate": asset.created_at.isoformat(),
                "size": asset.size,
            }
            decrypted.append(current_app_json)
            if app_name in decrypted_latest:
                current_latest_app_version: str = decrypted_latest[app_name]["version"]
                if Version(current_latest_app_version) < Version(
                    current_app_json["version"]
                ):
                    decrypted_latest[app_name] = current_app_json
            else:
                decrypted_latest[app_name] = current_app_json

    decrypted_json_all = {
        "name": "ZMyApps Decrypted",
        "identifier": "zmyapps.decrypted",
        "iconURL": f"{worker_base_url}/icon.png",
        "apps": sorted(decrypted, key=lambda p: p["versionDate"], reverse=True),
    }

    with open("./generated/decrypted.json", "w") as file:
        json.dump(decrypted_json_all, file)

    decrypted_json_latest = {
        "name": "ZMyApps Latest Decrypted",
        "identifier": "zmyapps.decrypted.latest",
        "iconURL": f"{worker_base_url}/icon.png",
        "apps": sorted(
            decrypted_latest.values(), key=lambda p: p["versionDate"], reverse=True
        ),
    }

    with open("./generated/decryptedlatest.json", "w") as file:
        json.dump(decrypted_json_latest, file)


def main():
    generate_decrypted()


if __name__ == "__main__":
    main()
