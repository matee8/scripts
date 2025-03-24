#!/usr/bin/env python3

import csv
import datetime
from http import cookiejar
import json
import sys
import typing
from urllib import error, parse, request

BASE_URL = "https://vszc-petofi.e-kreta.hu/api" \
    "/CalendarApi/GetTanariOrarendOrarendiorakEsTanorak"
PARAMS = {
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
FILENAME = "output.csv"


def read_token() -> tuple[str, str]:
    print("1. Log in to 'Kréta'.")
    print("2. Press 'Ctrl+Shift+I'.")
    print("3. Go to the 'Haladási Napló'")
    print("4. Go to the 'Storage'/'Application' tab.")
    print("5. In the left sidebar, expand 'Cookies'.")
    print("6. Find the 'Kréta' domain (https://*.e-kreta.hu).")
    print("7. Look for the cookie named 'kreta.application'.")
    print("8. Copy the 'Value' field of this cookie.")

    token = input("Enter the copied value: ").strip()
    if not token:
        raise ValueError("Token cannot be empty")

    print("9. Go to the 'Debugger' tab.")
    print("10. In the left sidebar, expand 'Orarend'.")
    print("11. Click on 'TanariOrarend'.")
    print("12. Press 'Ctrl+F' and search for 'tanarId: setCalendarTanarId'")
    print("13. Copy the parameter of the function.")

    teacher_id = input("Enter the copied value: ").strip()
    if not teacher_id:
        raise ValueError("Teacher ID cannot be empty.")

    return (token, teacher_id)


def create_request(
        token: str,
        teacher_id: str,
        start: datetime.datetime,
        end: datetime.datetime,
        url: str = BASE_URL,
        params: dict[str,
                     typing.Any] = PARAMS) -> tuple[str, cookiejar.CookieJar]:
    parsed_url = parse.urlparse(url)

    if not parsed_url.scheme:
        raise ValueError("URL must include a scheme")

    domain = parsed_url.netloc
    if not domain:
        raise ValueError("URL must include a domain")

    path = parsed_url.path or "/"

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
        secure=False,
        expires=None,
        discard=True,
        comment=None,
        comment_url=None,
        rest={},
        rfc2109=False,
    )

    cookies = cookiejar.CookieJar()

    cookies.set_cookie(cookie)

    params["start"] = start.strftime("%Y-%m-%d")
    params["end"] = end.strftime("%Y-%m-%d")
    params["tanarId"] = teacher_id

    encoded_params = parse.urlencode(params)

    new_url = parse.urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        encoded_params,
        parsed_url.fragment,
    ))

    return (new_url, cookies)


def send_request(cookies: cookiejar.CookieJar,
                 url: str) -> dict[str, dict[str, int]]:
    opener = request.build_opener(request.HTTPCookieProcessor(cookies))

    res = {}

    with opener.open(url) as response:
        content = response.read().decode("utf-8", errors="replace")
        parsed_data = json.loads(content)
        for elem in parsed_data:
            if elem["color"] == "#60BF55":
                lesson = elem["title"].split("\n")[0]
                date = datetime.datetime.fromisoformat(
                    elem["datum"]).strftime("%Y. %m. %d")
                daily_lessons = res.get(date, {})
                daily_lessons[lesson] = daily_lessons.get(lesson, 0) + 1
                res[date] = daily_lessons

    return res


def print_to_csv(lessons: dict[str, dict[str, int]],
                 filename: str = FILENAME) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["date", "lesson name", "daily count", "class"])
        for day, daily_lessons in lessons.items():
            for title, count in daily_lessons.items():
                split_title = title.split("-")
                name = split_title[0].strip()
                group = split_title[1].strip()
                writer.writerow([day, name, count, group])


def main():
    try:
        if len(sys.argv) != 3:
            raise ValueError(
                "Usage: python3 create_attendence.py <YEAR> <MONTH>")

        year = int(sys.argv[1])
        month = int(sys.argv[2])

        token, teacher_id = read_token()

        start_date = datetime.datetime(year, month, 1)

        if month == 12:
            end_date = datetime.datetime(year + 1, 1, 1)
        else:
            end_date = datetime.datetime(year, month + 1, 1)

        url, cookies = create_request(token, teacher_id, start_date, end_date)

        lessons = send_request(cookies, url)

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
    except IndexError as err:
        print(f"Invalid data: {err}")
    except csv.Error as err:
        print(f"CSV formatting failed: {err}")
    except SystemExit:
        print("Exiting.")
    except Exception as err:
        print(f"Unexpected error: {str(err)}")


if __name__ == "__main__":
    main()
