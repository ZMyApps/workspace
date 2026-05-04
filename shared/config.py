import sys
import tomllib
from pathlib import Path
from pprint import pprint

from shared.github import GitHubRepo

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR.parent / "config.toml"
_config_data = {}

try:
    with open(CONFIG_PATH, "rb") as file:
        _config_data = tomllib.load(file)
except FileNotFoundError:
    print(f"Error: Configuration file '{CONFIG_PATH}' not found.")
    sys.exit(1)
except tomllib.TOMLDecodeError as e:
    print(f"Error parsing TOML in '{CONFIG_PATH}': {e}")
    sys.exit(1)

build_archive_repo = GitHubRepo(_config_data["build_archive_repo"])
ipa_archive_repo = GitHubRepo(_config_data["ipa_archive_repo"])
tweak_archive_repo = GitHubRepo(_config_data["tweak_archive_repo"])

worker_base_url = _config_data["worker_base_url"]


def get_app_config(name=None, bundle_identifier=None):
    if name:
        if name not in _config_data["apps"]:
            print("[get_app_config(name=)]", name, "not found")
            return None
        current_config = _config_data["apps"][name]
        current_config["name"] = name
        return current_config
    elif bundle_identifier:
        for app_name in _config_data["apps"]:
            current_config = _config_data["apps"][app_name]
            if bundle_identifier == current_config["bundle_identifier"]:
                current_config["name"] = app_name
                return current_config
        print("[get_app_config(bundleIdentifier=)]", name, "not found")
        return None


if __name__ == "__main__":
    pprint(_config_data)
