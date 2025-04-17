#!/usr/bin/python3

from argparse import ArgumentParser, Namespace
from pathlib import Path
import subprocess
from subprocess import CompletedProcess
import sys


def _run_command(cmd: list[str],
                 cwd: Path,
                 description: str,
                 interactive: bool = False) -> CompletedProcess | None:
    try:
        print(f"Running command: {' '.join(cmd)} in {cwd.name}. "
              f"Interactive: {interactive}")
        result: CompletedProcess = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=not interactive,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode != 0:
            print(f"Error updating {cwd.name}", file=sys.stderr)

            if result.stderr:
                print(f"{description} error output: {result.stderr.strip()}",
                      file=sys.stderr)

            if result.stdout:
                print(
                    f"{description} standard output: {result.stdout.strip()}",
                    file=sys.stderr)

            return None
        return result
    except FileNotFoundError:
        print(f"Error: '{cmd[0]}' command not found.", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: Error running {description} for {cwd.name}: {e}",
              file=sys.stderr)
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)


def _main():
    parser = ArgumentParser(
        description=
        "Check for updates in Git repositiories within a base directory. " \
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

    for item_path in args.base_directory.iterdir():
        if item_path.is_dir():
            if not (item_path / ".git").is_dir():
                print(f"Skipping non-Git directory: {item_path.name}")
                continue

            try:
                git_result: CompletedProcess | None = _run_command(
                    ["git", "pull"], item_path, "'git pull'")

                if git_result is None:
                    continue

                if "Already up to date." in git_result.stdout:
                    print(f"No updates in {item_path.name}")
                    continue

                print(f"Updates pulled in {item_path.name}")
                print(f"Attempting to build and install {item_path.name} " \
                      "with 'makepkg -sirc'")

                makepkg_result: CompletedProcess | None = _run_command(
                    cmd=["makepkg", "-sirc"],
                    cwd=item_path,
                    description="'makepkg'",
                    interactive=True)

                if makepkg_result is None:
                    continue

                if makepkg_result.returncode == 0:
                    print(f"Successfully built and installed {item_path.name}")

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
