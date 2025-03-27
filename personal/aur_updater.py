#!/usr/bin/python3

import argparse
import os
import pathlib
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(
        description=
        "Check for updates in Git repositiories within a base directory." \
        "(e.g., AUR packages)",
    )
    parser.add_argument(
        "base_directory",
        type=pathlib.Path,
        help="The base directory containing the Git repositiories to check.",
    )

    args: argparse.Namespace = parser.parse_args()
    base_dir: pathlib.Path = args.base_directory

    if not base_dir.exists():
        print(f"Error: Base directory not found: {base_dir}", file=sys.stderr)
        sys.exit(1)

    if not base_dir.is_dir():
        print(f"Error: Provided path is not a directory: {base_dir}",
              file=sys.stderr)
        sys.exit(1)

    try:
        list(base_dir.iterdir())
    except PermissionError:
        print(f"Error: Permission denied to read directory: {base_dir}",
              file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: Error accessing directory {base_dir}: {e}",
              file=sys.stderr)
        sys.exit(1)

    print(f"Checking for repositiories under: {base_dir.resolve()}")

    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            os.chdir(item_path)
            print(f"Checking for updates in: {item}")

            result = subprocess.run(["git", "pull"],
                                    capture_output=True,
                                    text=True)

            if "Already up to date." not in result.stdout:
                print(f"Updates pulled in: {item}")
                print(result.stdout)
            else:
                print(f"No updates in: {item}")


if __name__ == "__main__":
    main()
