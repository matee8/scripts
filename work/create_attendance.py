#!/usr/bin/env python3

import argparse
import csv
import datetime
import json
import pathlib
import typing
import sys
from http import cookiejar
from urllib import parse, request, error

_BASE_URL: typing.Final[str] = (
    "https://vszc-petofi.e-kreta.hu/api"
    "/CalendarApi/GetTanariOrarendOrarendiorakEsTanorak")

_BASE_PARAMS: typing.Final[dict[str, typing.Any]] = {
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

_DEFAULT_FILENAME: typing.Final[pathlib.Path] = pathlib.Path("./output.csv")

_LESSON_COLOR_CODE: typing.Final[str] = "#60BF55"

LessonData = dict[str, dict[str, int]]


def _read_token_and_teacher_id() -> tuple[str, str]:
    print("Please follow these steps in your web browser:")
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
    if not teacher_id.isdigit():
        print("Warning: Teacher ID does not appear to be numeric.",
              file=sys.stderr)

    return token, teacher_id


def _build_api_request(
    token: str,
    teacher_id: str,
    start: datetime.datetime,
    end: datetime.datetime,
    base_url: str = _BASE_URL,
    base_params: dict[str, typing.Any] = _BASE_PARAMS
) -> tuple[str, cookiejar.CookieJar]:
    try:
        parsed_url: parse.ParseResult = parse.urlparse(base_url)
    except ValueError as e:
        raise ValueError(f"Invalid base URL '{base_url}': {e}") from e

    if not parsed_url.scheme:
        raise ValueError("URL must include a scheme")

    if not parsed_url.netloc:
        raise ValueError("URL must include a domain")

    domain: str = parsed_url.netloc
    path: str = parsed_url.path or "/"

    cookie = cookiejar.Cookie(
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
        secure=parsed_url.scheme == "https",
        expires=None,
        discard=True,
        comment=None,
        comment_url=None,
        rest={},
        rfc2109=False,
    )

    cookies = cookiejar.CookieJar()

    cookies.set_cookie(cookie)

    params = base_params.copy()
    params["start"] = start.strftime("%Y-%m-%d")
    params["end"] = end.strftime("%Y-%m-%d")
    params["tanarId"] = teacher_id

    encoded_params: str = parse.urlencode(params)

    new_url: str = parse.urlunparse(
        (parsed_url.scheme, parsed_url.netloc, parsed_url.path,
         parsed_url.params, encoded_params, parsed_url.fragment))

    return new_url, cookies


def _fetch_and_parse_schedule(cookies: cookiejar.CookieJar,
                              url: str) -> LessonData:
    opener: request.OpenerDirector = request.build_opener(
        request.HTTPCookieProcessor(cookies))

    aggregated_lessons: LessonData = {}

    if "?" in url:
        print(f"Fetching data from API: {url[:url.find('?')]}...")
    else:
        print(f"Fetching data from API: {url}...")

    try:
        req = request.Request(url)
        with opener.open(req, timeout=30) as response:
            if not 200 <= response.status < 300:
                raise error.HTTPError(url, response.status, response.reason,
                                      response.headers, None)

            try:
                response_bytes: bytes = response.read()
                response_text: str = response_bytes.decode("utf-8",
                                                           errors="replace")
                schedule_data: list[dict[str, typing.Any]] = json.loads(
                    response_text)
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                print(f"Error reading or parsing JSON from {url}: {e}",
                      file=sys.stderr)
                raise

            for entry in schedule_data:
                try:
                    if entry.get("color") != _LESSON_COLOR_CODE:
                        continue

                    lesson_title: str = entry.get("title", "").split("\n",
                                                                     1)[0]
                    date_str_iso: str | None = entry.get("datum")

                    if not lesson_title or not date_str_iso:
                        print(
                            "Warning: Skipping entry with missing title or "
                            f"date: {entry}",
                            file=sys.stderr)
                        continue

                    try:
                        lesson_date: datetime.datetime = (
                            datetime.datetime.fromisoformat(date_str_iso))
                        formatted_date: str = lesson_date.strftime(
                            "%Y. %m. %d.")
                    except ValueError as e:
                        print(
                            "Warning: Could not parse date for "
                            f"lesson {lesson_title}. Skipping entry. "
                            f"Error: {e}",
                            file=sys.stderr)
                        continue

                    daily_lessons: dict[str,
                                        int] = aggregated_lessons.setdefault(
                                            formatted_date, {})
                    daily_lessons[lesson_title] = daily_lessons.get(
                        lesson_title, 0) + 1
                except KeyError as e:
                    print(
                        "Warning: Skipping schedule entry due to missing "
                        f"key {e}.",
                        file=sys.stderr)
                    continue
                except Exception as e:
                    print(f"Warning: Unexpected error: {e}", file=sys.stderr)
                    continue
    except error.HTTPError as e:
        print(f"HTTP Error accessing API: {e.code} {e.reason}",
              file=sys.stderr)
        raise
    except error.URLError as e:
        print(f"Network error accessing Kréta API: {e.reason}",
              file=sys.stderr)
        raise
    except Exception:
        print("Warning: Unexpected error.", file=sys.stderr)
        raise

    return aggregated_lessons


def _write_lessons_to_csv(lessons: LessonData,
                          filename: pathlib.Path = _DEFAULT_FILENAME) -> None:
    print(f"Writing data to {filename}")

    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                ["date", "lesson_name", "daily_count", "class_group"])
            for date_str, daily_summary in sorted(lessons.items()):
                for lesson_title, count in daily_summary.items():
                    title_parts: list[str] = lesson_title.split("-", 1)

                    if len(title_parts) < 2:
                        raise ValueError(
                            "Lesson title does not match expected format.")

                    name: str = title_parts[0].strip()
                    group: str = title_parts[1].strip()

                    writer.writerow([date_str, name, count, group])

    except IOError as e:
        print(f"Error writing to file '{filename}': {e}", file=sys.stderr)
        raise
    except csv.Error as e:
        print(f"Error formatting data for CSV in file '{filename}': {e}",
              file=sys.stderr)
        raise
    except Exception as e:
        print(f"An unexpected error occurred during CSV writing: {e}",
              file=sys.stderr)
        raise


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Retrieves a teacher's schedule from Kreta"
                     "for a specific month and outputs it as a CSV."),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-y",
        "--year",
        type=int,
        required=True,
        help="The year of the report",
    )

    parser.add_argument(
        "-m",
        "--month",
        type=int,
        required=True,
        choices=range(1, 13),
        help="The month of the report",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        default=_DEFAULT_FILENAME,
        help="Path to the output CSV file.",
    )

    return parser.parse_args()


def _main():
    try:
        args: argparse.Namespace = _parse_arguments()

        output_path: pathlib.Path = args.output
        if output_path.parent != pathlib.Path(
                ".") and not output_path.parent.exists():
            print(f"Creating output directory: {output_path.parent}")
            output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            token: str
            teacher_id: str
            token, teacher_id = _read_token_and_teacher_id()
        except (ValueError, EOFError) as e:
            print(f"Error getting credentials: {e}", file=sys.stderr)
            sys.exit(1)

        try:
            start_date = datetime.datetime(args.year, args.month, 1)

            if args.month == 12:
                end_date = datetime.datetime(args.year + 1, 1, 1)
            else:
                end_date = datetime.datetime(args.year, args.month + 1, 1)
        except ValueError as e:
            print(f"Invalid year or month: {e}", file=sys.stderr)
            sys.exit(1)

        try:
            url: str
            cookies: cookiejar.CookieJar
            url, cookies = _build_api_request(token, teacher_id, start_date,
                                              end_date)
        except ValueError as e:
            print(f"Error preparing API request: {e}", file=sys.stderr)
            sys.exit(1)

        try:
            print(
                f"Requesting schedule from: {start_date.strftime('%Y-%m-%d')} "
                f"to {end_date.strftime('%Y-%m-%d')}")

            lessons: LessonData = _fetch_and_parse_schedule(cookies, url)

            if not lessons:
                print("No lesson data found.", file=sys.stderr)
                sys.exit(0)
        except (error.URLError, json.JSONDecodeError, KeyError, ValueError,
                UnicodeDecodeError):
            print(
                "Failed to retrieve or parse schedule data. See details above.",
                file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)

        try:
            _write_lessons_to_csv(lessons, output_path)
            print(f"Successfully wrote attendance data to '{output_path}'.")
        except (IOError, csv.Error, ValueError):
            print("Failed to write data to CSV file.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred writing the CSV: {e}",
                  file=sys.stderr)
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\nAn unexpected critical error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _main()
