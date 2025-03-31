#!/usr/bin/python3

from argparse import ArgumentParser, Namespace
import os
from pathlib import Path
import subprocess
import sys


def _main():
    parser = ArgumentParser(
        description=
        "Check for updates in Git repositiories within a base directory." \
        "(e.g., AUR packages)",
    )
    parser.add_argument(
        "base_directory",
        type=Path,
        help="The base directory containing the Git repositiories to check.",
    )

    args: Namespace = parser.parse_args()

    if not args.base_directory.exists():
        print(f"Error: Base directory not found: {args.base_directory}",
              file=sys.stderr)
        sys.exit(1)

    if not args.base_directory.is_dir():
        print(
            f"Error: Provided path is not a directory: {args.base_directory}",
            file=sys.stderr)
        sys.exit(1)

    try:
        list(args.base_directory.iterdir())
    except PermissionError:
        print(
            "Error: Permission denied to read " \
            "directory: {args.base_directory}",
            file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: Error accessing directory {args.base_directory}: {e}",
              file=sys.stderr)
        sys.exit(1)

    print(f"Checking for repositiories under: {args.base_directory.resolve()}")

    for item in os.listdir(args.base_directory):
        item_path = os.path.join(args.base_directory, item)
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
    _main()
