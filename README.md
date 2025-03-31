# Automation scripts

This repository contains automation scripts designed to simplify repetitive
tasks across work, school, and personal projects.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Scripts Overview](#scripts-overview)
- [License](#license)

---

## Getting Started

1.  Clone the repository:
    ```bash
    git clone <your-repo-url>
    cd <repository-name>
    ```
2.  Ensure all prerequisites listed below are met.
3.  Make scripts executable if needed (e.g., `chmod +x work/psgdrive.sh`).

---

## Scripts Overview

### `work/create_attendence.py`

**Purpose**: Retrieves a teacher's schedule from Kreta and aggregates lesson
counts per day/class.

**Output**: `output.csv` with columns: `Date`, `Lesson Name`, `Count`,
`Class Group`.

**Usage**:

```bash
python3 ./work/create_attendance.py --year <YEAR> --month <MONTH>
```

**Requires**: `python`, `Kreta access`

### `work/psgdrive.sh`

**Purpose**: Automates mounting/unmounting Google Drive via `rclone` in a `tmux`
session.

**Usage**:

```bash
./work/psgdrive.sh <mount|umount>
```

**Requires**: `tmux`, `rclone`

### `personal/aur_updater.py`

**Purpose**: Checks for updates in local git repositories within a specified
directory. If a repository has updates, it attempts to automatically build
and install the package using `makepkg -sirc`.

**Usage**:

```bash
python3 ./personal/aur_updater.py ~/.cache/aur
```

**Requires**: `python`, `git`, `makepkg`

**Note**: This script will execute `pacman` and will prompt for your
administrator password. Run only on directories containing trusted package
sources.

---

## License
MIT License. See [LICENSE](LICENSE) for details.

---

> *Note*: Scripts are designed for personal use. Ensure compliance with platform
> terms of service (e.g., Kreta API usage).
