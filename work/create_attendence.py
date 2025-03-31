#!/usr/bin/env python3
"""
create_attendence.py
=====================

This module provides a script to fetch and process attendance data for a
teacher's schedule from the Kreta educational platform. It generates a CSV file
summarizing the number of lessons per day and class group.

**Purpose**:
-   Fetches schedule data via the Kreta API using a user-provided authentication
    token and teacher ID.
-   Processes the data to count lessons per day and class.
-   Outputs the results to a CSV file named 'output.csv'.

**Usage**:
Run the script with command-line arguments specifying the year and month (e.g.,
`python3 create_attendence.py 2024 9`).


**Required Inputs**:
1.  **Authentication Token**: Retrieved from the browser's storage (Kreta
    domain cookie).
2.  **Teacher ID**: Extracted from the browser's debugging tools.

**Output**:
A CSV file with columns: Date, Class Name, Lesson Count, Group Name.

**Dependencies**:
-   Python 3.6+ with `urllib`, `datetime`, `csv`, and `json` modules.
-   User must have access to the Kreta platform and follow instructions to
    obtain the token and teacher ID.

**Author**: matee8
**Date**: March 25, 2025
"""

import csv
from datetime import datetime
from http.cookiejar import CookieJar, Cookie
import json
import sys
from typing import Any
from urllib import error, parse, request
from urllib.parse import ParseResult
from urllib.request import OpenerDirector, HTTPCookieProcessor

BASE_URL: str = "https://vszc-petofi.e-kreta.hu/api" \
    "/CalendarApi/GetTanariOrarendOrarendiorakEsTanorak"
PARAMS: dict[str, Any] = {
    "osztalyCsoportId": -1,
    "tanuloId": -1,
    "teremId": -1,
    "kellCsengetesiRendMegjelenites": True,
    "csakOrarendiOra": False,
    "kellTanoranKivuliFoglalkozasok": False,
    "kellTevekenysegek": False,
    "kellTanevRendje": True,
    "szuresTanevRendjeAlapjan": False,
    "kellOraTemaTooltip": True,
}
FILENAME: str = "output.csv"


def read_token_and_teacher_id() -> tuple[str, str]:
    """
    Prompts the user to extract authentication token and teacher ID from the
    browser.

    Instructions guide the user through retrieving the 'kreta.application'
    cookie and teacher ID from browser developer tools. Validates inputs to
    ensure neither token nor teacher ID are empty.

    Returns:
        tuple[str, str]: A tuple containing the token and teacher ID.

    Raises:
        ValueError: If either the token or teacher ID is empty.
    """
    print("1. Log in to 'Kréta'.")
    print("2. Press 'Ctrl+Shift+I'.")
    print("3. Go to the 'Haladási Napló'")
    print("4. Go to the 'Storage'/'Application' tab.")
    print("5. In the left sidebar, expand 'Cookies'.")
    print("6. Find the 'Kréta' domain (https://*.e-kreta.hu).")
    print("7. Look for the cookie named 'kreta.application'.")
    print("8. Copy the 'Value' field of this cookie.")

    token: str = input("Enter the copied value: ").strip()
    if not token:
        raise ValueError("Token cannot be empty")

    print("9. Go to the 'Debugger' tab.")
    print("10. In the left sidebar, expand 'Orarend'.")
    print("11. Click on 'TanariOrarend'.")
    print("12. Press 'Ctrl+F' and search for 'tanarId: setCalendarTanarId'")
    print("13. Copy the parameter of the function.")

    teacher_id: str = input("Enter the copied value: ").strip()
    if not teacher_id:
        raise ValueError("Teacher ID cannot be empty.")

    return (token, teacher_id)


def create_request(
        token: str,
        teacher_id: str,
        start: datetime,
        end: datetime,
        url: str = BASE_URL,
        params: dict[str, Any] = PARAMS) -> tuple[str, CookieJar]:
    """
    Constructs the API request URL with parameters and authentication cookies.

    Args:
        token (str): Authentication token from 'kreta.application' cookie.
        teacher_id (str): Identifier for the teacher.
        start (datetime.datetime): Start date of the schedule period.
        end (datetime.datetime): End date of the schedule period.
        url (str, optional): Base API endpoint URL. Defaults to BASE_URL.
        params (dict, optional): API parameters. Defaults to PARAMS.

    Returns:
        tuple[str, CookieJar]: The URL and cookie jar for authentication.

    Raises:
        ValueError: If the URL lacks a scheme (e.g., 'http') or domain.
    """
    parsed_url: ParseResult = parse.urlparse(url)

    if not parsed_url.scheme:
        raise ValueError("URL must include a scheme")

    domain: str = parsed_url.netloc
    if not domain:
        raise ValueError("URL must include a domain")

    path: str = parsed_url.path or "/"

    cookie = Cookie(
        version=0,
        name="kreta.application",
        value=token,
        port=None,
        port_specified=False,
        domain=domain,
        domain_specified=True,
        domain_initial_dot=False,
        path=path,
        path_specified=True,
        secure=False,
        expires=None,
        discard=True,
        comment=None,
        comment_url=None,
        rest={},
        rfc2109=False,
    )

    cookies = CookieJar()

    cookies.set_cookie(cookie)

    params["start"] = start.strftime("%Y-%m-%d")
    params["end"] = end.strftime("%Y-%m-%d")
    params["tanarId"] = teacher_id

    encoded_params: str = parse.urlencode(params)

    new_url: str = parse.urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        encoded_params,
        parsed_url.fragment,
    ))

    return (new_url, cookies)


def send_request(cookies: CookieJar, url: str) -> dict[str, dict[str, int]]:
    """
    Sends the HTTP request to the Kreta API and processes the response.

    Args:
        cookies (CookieJar): Authentication cookies for the request.
        url (str): The fully constructed API endpoint URL.

    Returns:
        dict: Aggregated lesson data in the format {date: {lesson: count}}.

    Raises:
        URLError: If the network request fails.
        JSONDecodeError: If the API response is not valid JSON.
    """
    opener: OpenerDirector = request.build_opener(HTTPCookieProcessor(cookies))

    res: dict[str, dict[str, int]] = {}

    with opener.open(url) as response:
        content = response.read().decode("utf-8", errors="replace")
        parsed_data = json.loads(content)
        for elem in parsed_data:
            if elem["color"] == "#60BF55":
                lesson: str = elem["title"].split("\n")[0]
                date: str = datetime.fromisoformat(
                    elem["datum"]).strftime("%Y. %m. %d")
                daily_lessons: dict[str, int] = res.get(date, {})
                daily_lessons[lesson] = daily_lessons.get(lesson, 0) + 1
                res[date] = daily_lessons

    return res


def print_to_csv(lessons: dict[str, dict[str, int]],
                 filename: str = FILENAME) -> None:
    """
    Writes aggregated lesson data to a CSV file.

    Args:
        lessons (dict): Processed data in the format {date: {lesson: count}}.
        filename (str, optional): Output CSV filename. Defaults to 'output.csv'.

    Raises:
        ValueError: If lesson titles lack the required '-' separator.
        CSVError: If CSV formatting fails (e.g., file permissions).
    """
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["date", "lesson name", "daily count", "class"])
        for day, daily_lessons in lessons.items():
            for title, count in daily_lessons.items():
                split_title: list[str] = title.split("-")
                if len(split_title) < 2:
                    raise ValueError(
                        "Title must contain at least one '-' character")
                name: str = split_title[0].strip()
                group: str = split_title[1].strip()
                writer.writerow([day, name, count, group])


def main():
    """
    Entry point for the script. Handles command-line arguments and coordinates
    data fetching, processing, and output.

    Usage:
        python create_attendence.py <YEAR> <MONTH>

    Args:
        sys.argv[1] (int): Year for the schedule period (e.g., 2024).
        sys.argv[2] (int): Month for the schedule period (1-12).

    Raises:
        ValueError: For invalid input formats or missing arguments.
        KeyboardInterrupt: If the user cancels execution.
        (Other exceptions are handled with descriptive error messages.)
    """
    try:
        if len(sys.argv) != 3:
            raise ValueError(
                "Usage: python3 create_attendence.py <YEAR> <MONTH>")

        year = int(sys.argv[1])
        month = int(sys.argv[2])

        token: str
        teacher_id: str
        token, teacher_id = read_token_and_teacher_id()

        start_date = datetime(year, month, 1)

        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        url: str
        cookies: CookieJar
        url, cookies = create_request(token, teacher_id, start_date, end_date)

        lessons: dict[str, dict[str, int]] = send_request(cookies, url)

        print_to_csv(lessons)
        print(f"Attendence written to {FILENAME}.")
    except UnicodeEncodeError as err:
        print(f"Terminal write error: {err}")
    except EOFError as err:
        print(f"No user input given: {err}")
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Exiting.")
    except error.URLError as err:
        print(f"Network error: {err}")
    except json.JSONDecodeError as err:
        print(f"Failed to decode payload: {err}")
    except ValueError as err:
        print(f"Input error: {err}")
    except KeyError as err:
        print(f"Invalid payload: {err}")
    except PermissionError as err:
        print(f"Permissions lacking: {err}")
    except csv.Error as err:
        print(f"CSV formatting failed: {err}")


if __name__ == "__main__":
    main()
