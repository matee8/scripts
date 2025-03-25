# Automation scripts

This repository contains automation scripts designed to simplify repetitive
tasks across work, school, and personal projects.

---

## Table of Contents

- [Scripts Overview](#scripts-overview)
- [License](#license)

---

## Scripts Overview

### 1. `work/create_attendence.py`

**Purpose**: Retrieves a teacher's schedule from Kreta and aggregates lesson
counts per day/class.

**Output**: `output.csv` with columns: `Date`, `Lesson Name`, `Count`,
`Class Group`.

**Usage**:

```bash
python3 ./work/create_attendence.py <YEAR> <MONTH>
# Example: python3 create_attendence.py 2025 3
```

### 2. `work/psgdrive.sh`

**Purpose**: Automates mounting/unmounting Google Drive via `rclone` in a `tmux`
session.

**Usage**:

```bash
./work/psgdrive.sh <mount|umount>
```

---

## License
MIT License. See [LICENSE](LICENSE) for details.

---

> *Note*: Scripts are designed for personal use. Ensure compliance with platform
> terms of service (e.g., Kreta API usage).
