import argparse
import os
import subprocess
import tempfile
from urllib.parse import urlparse

import requests
from githubkit.versions.latest.models import ReleaseAsset

from shared.config import build_archive_repo, get_tweak_config
from shared.cydia import CydiaRepo
from shared.github import GitHubRepo, github_client
from shared.ipa import extract_ipa_metadata
from shared.repo import decrypted_repo


def download_file(url: str, folder_path: str, file_name: str | None = None):
    if not file_name:
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)

    file_path = os.path.join(folder_path, file_name)

    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    return file_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tweak_name")
    parser.add_argument("--app-version")
    parser.add_argument("--note")
    args = parser.parse_args()

    # Args
    note = args.note

    # Get config
    tweak_config = get_tweak_config(args.tweak_name)
    if not tweak_config:
        raise Exception(args.tweak_name, "tweak not found")

    # Get IPA Link
    decrypted_app_download_url = None
    decrypted_repo.fetch()
    if args.app_version and args.app_version != "latest":
        app_info = decrypted_repo.get_app(
            name=tweak_config["app_name"], version=args.app_version
        )
        decrypted_app_download_url = app_info["downloadURL"]
    else:
        app_info = decrypted_repo.get_latest_app(name=tweak_config["app_name"])
        decrypted_app_download_url = app_info["downloadURL"]

    # Get Debs Link
    deb_download_urls = []
    tweak_use_version = ""
    if tweak_config and "debs" in tweak_config:
        for deb in tweak_config["debs"]:
            match deb["method"]:
                case "cydia_repo_latest":
                    repo = CydiaRepo(deb["repo"])
                    package = repo.get_latest_package(bundle_identifier=deb["package"])
                    download_url = package.download_url
                    deb_download_urls.append(download_url)
                    if "use_version" in deb and deb["use_version"]:
                        tweak_use_version = package["Version"]
                case "cydia_repo_version":
                    repo = CydiaRepo(deb["repo"])
                    package = repo.get_package(
                        bundle_identifier=deb["package"], version=deb["version"]
                    )
                    download_url = package.download_url
                    deb_download_urls.append(download_url)
                    if "use_version" in deb and deb["use_version"]:
                        tweak_use_version = deb["version"]
                case "github_release_latest":
                    repo = GitHubRepo(deb["repo"])
                    asset = repo.get_release_asset(
                        latest=True, asset_name_endswith=deb["endswith"]
                    )
                    download_url = asset["url"]
                    deb_download_urls.append(download_url)
                    if "use_version" in deb and deb["use_version"]:
                        tweak_use_version = asset["tag"]
                case "github_release_version":
                    repo = GitHubRepo(deb["repo"])
                    asset = repo.get_release_asset(
                        tag=deb["version"], asset_name_endswith=deb["endswith"]
                    )
                    download_url = asset["url"]
                    deb_download_urls.append(download_url)
                    if "use_version" in deb and deb["use_version"]:
                        tweak_use_version = deb["version"]

    with tempfile.TemporaryDirectory() as tmpdirname:
        # Download ipa
        print("Downloading ipa")
        ipa_path = download_file(url=decrypted_app_download_url, folder_path=tmpdirname)
        ipa_metadata = extract_ipa_metadata(ipa_path)
        # Download debs
        deb_paths = []
        for deb_download_url in deb_download_urls:
            print("Downloading deb")
            deb_path = download_file(url=deb_download_url, folder_path=tmpdirname)
            deb_paths.append(deb_path)

        # Inject
        injected_path = os.path.join(tmpdirname, "injected.ipa")
        subprocess.run(
            [
                "cyan",
                "--input",
                ipa_path,
                "--output",
                injected_path,
                "--remove-supported-devices",
                "--no-watch",
                "--remove-extensions",
                "-f",
                *deb_paths,
            ],
            check=True,
            cwd=tmpdirname,
        )

        # Custom: ApolloICA Liquid Glass Patching
        if args.tweak_name == "ApolloICA":
            apollo_repo_dir = os.path.join(tmpdirname, "Apollo-ImprovedCustomApi")
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth=1",
                    "https://github.com/ZMyApps/Apollo-ImprovedCustomApi.git",
                    apollo_repo_dir,
                ],
                check=True,
            )
            apolloica_patch_script_path = os.path.join(apollo_repo_dir, "patch.sh")
            subprocess.run(
                [
                    "bash",
                    apolloica_patch_script_path,
                    injected_path,
                    "--output",
                    "apollo_ica_patched.ipa",
                    "--liquid-glass",
                ],
                check=True,
                cwd=tmpdirname,
            )
            os.replace(
                os.path.join(tmpdirname, "apollo_ica_patched.ipa"), injected_path
            )
            note = "LiquidGlass"

        # Upload
        github_run_number = os.getenv("GITHUB_RUN_NUMBER")
        if not tweak_use_version and github_run_number:
            tweak_use_version = github_run_number

        if note:
            release_tag = f"{tweak_config['app_name']}_{ipa_metadata['version']}_{tweak_config['name']}_{tweak_use_version}_{note}"
        else:
            release_tag = f"{tweak_config['app_name']}_{ipa_metadata['version']}_{tweak_config['name']}_{tweak_use_version}"
        release = github_client.rest.repos.create_release(
            owner=build_archive_repo.owner,
            repo=build_archive_repo.repo,
            tag_name=release_tag,
        )
        print("Created release")
        with open(injected_path, "rb") as f:
            file_name = f"{release_tag}.ipa"
            github_client.request(
                "POST",
                release.parsed_data.upload_url.split("{?")[0],
                params={"name": file_name},
                content=f.read(),
                headers={"Content-Type": "application/octet-stream"},
                response_model=ReleaseAsset,
            )

            print("Uploaded")


if __name__ == "__main__":
    main()
