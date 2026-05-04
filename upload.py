import argparse
import sys
from pathlib import Path

from shared.config import get_app_config, ipa_archive_repo
from shared.confirm import confirm
from shared.github import github_client
from shared.ipa import extract_ipa_metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ipa_path")
    parser.add_argument("--note")
    args = parser.parse_args()

    ipa_path = Path(args.ipa_path)
    if not ipa_path.is_file():
        print(f"Error: IPA file not found: {ipa_path}", file=sys.stderr)
        sys.exit(1)

    metadata = extract_ipa_metadata(str(ipa_path))
    app_config = get_app_config(bundle_identifier=metadata["bundle_identifier"])

    release_tag = f"{app_config['name']}_{metadata['version']}"
    notes = args.note
    if "-eeveedecrypter" in ipa_path.name:
        notes = f"eeveedecrypter-{notes}" if notes else "eeveedecrypter"
    elif "-Decrypted" in ipa_path.name:
        notes = f"armconverter-{notes}" if notes else "armconverter"
    elif "_decrypt_" in ipa_path.name:
        notes = f"anyipa-{notes}" if notes else "anyipa"
    elif "-AppAssassin" in ipa_path.name:
        notes = f"appassassin-{notes}" if notes else "appassassin"

    if notes:
        release_tag = f"{app_config['name']}_{metadata['version']}_{notes}"

    print("=======================")
    print(f"\n  \033[95m{release_tag}.ipa\033[0m\n")

    if confirm(default=True):
        release = github_client.rest.repos.create_release(
            owner=ipa_archive_repo.split("/")[0],
            repo=ipa_archive_repo.split("/")[1],
            tag_name=release_tag,
        )
        with open(ipa_path, "rb") as f:
            asset = github_client.rest.repos.upload_release_asset(
                owner=ipa_archive_repo.split("/")[0],
                repo=ipa_archive_repo.split("/")[1],
                release_id=release.parsed_data.id,
                name=f"{release_tag}.ipa",
                data=f.read(),
            )
            print("Uploaded", asset.parsed_data.browser_download_url)
    print("=======================")


if __name__ == "__main__":
    main()
