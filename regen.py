#!/usr/bin/env -S uv run

from shared.dispatch import dispatch_json


def main():
    dispatch_json()


if __name__ == "__main__":
    main()
