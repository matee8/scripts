#!/usr/bin/python3

from argparse import ArgumentParser, Namespace
from pathlib import Path
import subprocess
from subprocess import CompletedProcess
import sys


def _main():
    parser = ArgumentParser(
        description=
        "Check for updates in Git repositiories within a base directory. " \
        "(e.g., AUR packages)",
    )
    parser.add_argument(
        "--base-directory",
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

    try:
        list(args.base_directory.iterdir())
    except PermissionError:
        print(
            "Error: Permission denied to read " \
            f"directory: {args.base_directory}",
            file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: Error accessing directory {args.base_directory}: {e}",
              file=sys.stderr)
        sys.exit(1)

    for item_path in args.base_directory.iterdir():
        if item_path.is_dir():
            if not (item_path / ".git").is_dir():
                print(f"Skipping non-Git directory: {item_path.name}")
                continue

            try:
                result: CompletedProcess[str] = subprocess.run(
                    ["git", "pull"],
                    cwd=item_path,
                    capture_output=True,
                    text=True,
                    check=False,
                    encoding="utf-8",
                    errors="replace",
                )

                if result.returncode != 0:
                    print(f"Error updating {item_path.name}", file=sys.stderr)
                    if result.stderr:
                        print(f"Git error output: {result.stderr.strip()}",
                              file=sys.stderr)
                    if result.stdout:
                        print(f"Git standard output: {result.stdout.strip}",
                              file=sys.stderr)
                    continue

                if "Already up to date." not in result.stdout:
                    print(f"Updates pulled in {item_path.name}")
                else:
                    print(f"No updates in {item_path.name}")

            except FileNotFoundError:
                print("Error: 'git' command not found.", file=sys.stderr)
                sys.exit(1)
            except OSError as e:
                print(f"Error: Error running git for {item_path.name}: {e}",
                      file=sys.stderr)
            except Exception as e:
                print(f"Error: Unexpected error: {e}", file=sys.stderr)


if __name__ == "__main__":
    _main()
