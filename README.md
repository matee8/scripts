# Automation scripts

This repository contains a collection of automation scripts designed to simplify
and streamline repetitive tasks across various domains including work, school,
and personal projects.

# Overview

The primary goal of this collection is to provide practical, ready-to-use
scripts that reduce manual effort and improve efficiency for common workflows.
Each script is self-contained within its respective category (e.g., `work`,
`personal`) and addresses a specific automation need.

# Getting Started

## Prerequisites

The prerequisites vary per script. Common requirements include:

-   A Unix-like shell environment (e.g., Bash) for `.sh` scripts.
-   Python 3.x for `.py` scripts.
-   Specific tools or access credentials as listed for each script (e.g., 
    `rclone`, `tmux`, `git`, `makepkg`, Kreta API access).

## Installation & Setup

1.  Clone the repository.

    ```bash
    git clone https://github.com/matee8/scripts.git
    cd scripts
    ```

2.  Ensure Dependencies.

    Verify that all prerequisites and dependencies for the specific script(s)
    you intend to use are installed on your system.

3.  Make Scripts Executable (if needed).

    For shell scripts, you might need to grant execute permissions:

    ```bash
    chmod +x work/psgdrive.sh
    # Add chmod +x for other shell scripts as necessary
    ```

    Python scripts can typically be run directly with `python3 ...` without
    needing explicit execute permissions, but it can be convenient.

# Project Structure

The repository is organized by the domain of application for the scripts:

```
.
├── work/
│   ├── create_attendence.py  # Script for Kreta teacher schedule aggregation
│   └── psgdrive.sh           # Script for managing Google Drive mount via rclone and tmux
├── personal/
│   └── aur_updater.py        # Script for checking and updating AUR packages
├── LICENSE                   # Project licensing information
└── README.md                 # This README file
```

# Scripts Overview & Usage

This section details each script, its purpose, how to run it, and its specific
requirements.

## `work/create_attendence.py`

**Purpose**:

This Python script retrieves a teacher's schedule from the Kreta system for a
specified year and month. It then aggregates the lesson counts per day and
class group, providing a summary of teaching activities.

**Output**:

The script generates a CSV file (default: `output.csv`) with the following columns:

-   `Date`: The date of the lessons.
-   `Lesson Name`: The name or subject of the lesson.
-   `Count`: The number of lessons for that subject on that date for the class.
-   `Class Group`: The specific class group.

**Usage**:

```bash
python3 ./work/create_attendance.py --year <YEAR> --month <MONTH> --output <OUTPUT_FILE_PATH>
```

**Parameters**:

```plaintext
usage: create_attendance.py [-h] -y YEAR -m {1,2,3,4,5,6,7,8,9,10,11,12} [-o OUTPUT]

Retrieves a teacher's schedule from Kretafor a specific month and outputs it as a CSV.

options:
  -h, --help            show this help message and exit
  -y, --year YEAR       The year of the report (default: None)
  -m, --month {1,2,3,4,5,6,7,8,9,10,11,12}
                        The month of the report (default: None)
  -o, --output OUTPUT   Path to the output CSV file. (default: output.csv)
```

**Requires**:

-   Python
-   Access credentials and ability to interact with the Kreta API (implicitly
    handled by the script's internal logic, ensure you have valid session/token
    means if required by the Kreta system).

## `work/psgdrive.sh`

**Purpose**:

This shell script automates the process of mounting and unmounting a Google
Drive remote configured with `rclone`. It manages these operations within a
detached `tmux` session for background operation.

**Usage**:

```bash
./work/psgdrive.sh <action>
```

**Parameters**:

-   `<action>`: (Required) Specifies the operation to perform.

    -   `mount`: Mounts the Google Drive.
    -   `umount`: Unmounts the Google Drive.

**Requires**:

-   `tmux`: Terminal multiplexer.
-   `rclone`: Command-line program to manage files on cloud storage. Ensure
    `rclone` is configured with a Google Drive remote.

## `personal/aur_updater.py`

**Purpose**:

This Python script is designed for Arch Linux users who manage AUR (Arch User
Repository) packages through local git repositories. It checks for updates in
all local git repositories located within a specified parent directory. If a
repository has unpulled upstream changes, the script attempts to automatically
build and install the package using `makepkg -sirc`.

**Usage**:

```bash
python3 ./personal/aur_updater.py <AUR_CACHE_DIRECTORY>
```

**Parameters**:

```plaintext
usage: aur_updater.py [-h] base_directory

Check for updates in Git repositiories within a base directory. (e.g., AUR packages) and build/install them.

positional arguments:
  base_directory  The base directory containing the Git repositiories to check.

options:
  -h, --help      show this help message and exit
```

**Requires**:

-   Python
-   `git`
-   `makepkg`
-   `pacman`

**Important Note**:

This script will execute `makepkg -sirc`, which in turn may invoke `pacman` to
install dependencies and the package itself. This process will likely prompt for
your administrator (sudo) password. **Only run this script on directories
containing AUR package sources that you trust completely.**

## License

This project is licensed under the [MIT License](LICENSE).

> *Disclaimer*: These scripts are provided "as-is" and are primarily designed
> for personal use. Ensure you understand what each script does before running
> it, especially those requiring elevated privileges or interacting with
> external services. Always ensure compliance with the terms of service of any
> platform (e.g., Kreta API) these scripts might interact with.
