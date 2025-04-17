#!/usr/bin/python3

import argparse
import pathlib
import typing
import subprocess
import sys


def _run_command(
        cmd: typing.List[str],
        cwd: pathlib.Path,
        description: str,
        interactive: bool = False
) -> typing.Optional[subprocess.CompletedProcess]:
    try:
        print(f"Running command: {' '.join(cmd)} in {cwd.name}. "
              f"Interactive: {interactive}.")
        result: subprocess.CompletedProcess = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=not interactive,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace")

        if result.returncode != 0:
            print(
                f"Error: {description} for {cwd.name} failed with exit code "
                f"{result.returncode}.",
                file=sys.stderr)

            if result.stderr:
                print(f"Error output: {result.stderr.strip()}",
                      file=sys.stderr)

            if result.stdout:
                print(f"Standard output: {result.stdout.strip()}",
                      file=sys.stderr)

            return None
        return result
    except FileNotFoundError:
        print(f"Error: '{cmd[0]}' command not found.", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: OS error running {description} for {cwd.name}: {e}",
              file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Unexpected error running {description}: {e}",
              file=sys.stderr)
        return None


def _main():
    parser = argparse.ArgumentParser(
        description=
        "Check for updates in Git repositiories within a base directory. "
        "(e.g., AUR packages) and build/install them.")
    parser.add_argument(
        "base_directory",
        type=pathlib.Path,
        help="The base directory containing the Git repositiories to check.")

    args: argparse.Namespace = parser.parse_args()

    base_dir: pathlib.Path = args.base_directory.resolve()

    if not base_dir.exists():
        print(f"Error: Base directory not found: {base_dir}.", file=sys.stderr)
        sys.exit(1)

    if not base_dir.is_dir():
        print(f"Error: Provided path is not a directory: {base_dir}.",
              file=sys.stderr)
        sys.exit(1)

    try:
        _ = list(base_dir.iterdir())
    except PermissionError:
        print("Error: Permission denied to read directory: {base_dir}.",
              file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: Error accessing directory {base_dir}: {e}",
              file=sys.stderr)
        sys.exit(1)

    for item_path in base_dir.iterdir():
        if not item_path.is_dir():
            continue

        if not (item_path / ".git").is_dir():
            print(f"Skipping non-Git directory: {item_path.name}.")
            continue

        git_result: typing.Optional[
            subprocess.CompletedProcess] = _run_command(["git", "pull"],
                                                        item_path,
                                                        "'git pull'")

        if git_result is None:
            continue

        if "Already up to date." in git_result.stdout:
            print(f"No updates in {item_path.name}.")
            continue

        print(f"Updates pulled in {item_path.name}.")
        print(f"Attempting to build and install {item_path.name} " \
                "with 'makepkg -sirc'.")

        makepkg_result: typing.Optional[
            subprocess.CompletedProcess] = _run_command(
                cmd=["makepkg", "-sirc"],
                cwd=item_path,
                description="'makepkg'",
                interactive=True)

        if makepkg_result is None:
            print(f"Build/install failed for {item_path.name}.",
                  file=sys.stderr)
            continue

        print(f"Successfully built and installed {item_path.name}.")

        clean_result: typing.Optional[
            subprocess.CompletedProcess] = _run_command(
                ["git", "clean", "-dfx"], item_path, "'git clean -dfx'")

        if clean_result is None:
            print(f"Cleanup failed for {item_path.name}", file=sys.stderr)
            continue

        print(f"Cleaned untracked files in {item_path.name}")


if __name__ == "__main__":
    _main()
