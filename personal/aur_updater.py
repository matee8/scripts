#!/usr/bin/python3

import os
import subprocess

def main():
    base_directory = os.getcwd()

    for item in os.listdir(base_directory):
        item_path = os.path.join(base_directory, item)
        if os.path.isdir(item_path):
            os.chdir(item_path)
            print(f"Checking for updates in: {item}")

            result = subprocess.run(['git', 'pull'], capture_output=True, text=True)

            if "Already up to date." not in result.stdout:
                print(f"Updates pulled in: {item}")
                print(result.stdout)
            else:
                print(f"No updates in: {item}")

if __name__ == "__main__":
    main()
