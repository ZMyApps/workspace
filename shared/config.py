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

workspace_repo = GitHubRepo(_config_data["workspace_repo"])
build_archive_repo = GitHubRepo(_config_data["build_archive_repo"])
ipa_archive_repo = GitHubRepo(_config_data["ipa_archive_repo"])
tweak_archive_repo = GitHubRepo(_config_data["tweak_archive_repo"])


def get_app_config(name=None, bundle_identifier=None):
    if name:
        current_config = next(
            (config for config in _config_data["apps"] if config["name"] == name), None
        )
        if current_config is None:
            print("get_app_config", "name", name, "None")
        return current_config
    elif bundle_identifier:
        current_config = next(
            (
                config
                for config in _config_data["apps"]
                if config["bundle_identifier"] == bundle_identifier
            ),
            None,
        )
        if current_config is None:
            print("get_app_config", "bundle_identifier", bundle_identifier, "None")
        return current_config


def get_tweak_config(name):
    current_config = next(
        (config for config in _config_data["tweaks"] if config["name"] == name), None
    )
    if current_config is None:
        print("get_tweak_config", "name", name, "None")
    else:
        current_config["app"] = get_app_config(name=current_config["app_name"])
    return current_config


if __name__ == "__main__":
    pprint(_config_data)
