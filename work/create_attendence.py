#!/usr/bin/env python3

import csv
import datetime
from http import cookiejar
import json
import sys
import typing
from urllib import error, parse, request

URL = "https://vszc-petofi.e-kreta.hu/api" \
    "/CalendarApi/GetTanariOrarendOrarendiorakEsTanorak"
PARAMS = {
    "tanarId": 700936,
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


def show_guide():
    print("1. Log in to 'Kréta'.")
    print("2. Press 'Ctrl+Shift+I'.")
    print("3. Go to the 'Storage'/'Application' tab.")
    print("4. In the left sidebar, expand 'Cookies'.")
    print("5. Find the 'Kréta' domain (https://*.e-kreta.hu).")
    print("6. Look for the cookie named 'kreta.application'.")
    print("7. Copy the 'Value' field of this cookie.")


def read_token() -> str:
    token = input("Enter the token: ").strip()
    if not token:
        raise ValueError("Token cannot be empty")

    return token


def send_request(
        token: str,
        start: str,
        end: str,
        url: str = URL,
        params: dict[str, typing.Any] = PARAMS) -> dict[str, dict[str, int]]:
    cj = cookiejar.CookieJar()

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

    cj.set_cookie(cookie)

    opener = request.build_opener(request.HTTPCookieProcessor(cj))

    params["start"] = start
    params["end"] = end

    encoded_params = parse.urlencode(params)

    new_url = parse.urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        encoded_params,
        parsed_url.fragment,
    ))

    res = {}

    with opener.open(new_url) as response:
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
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
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

        show_guide()
        token = read_token()

        start_date = datetime.datetime(year, month, 1)

        if month == 12:
            end_date = datetime.datetime(year + 1, 1, 1)
        else:
            end_date = datetime.datetime(year, month + 1, 1)

        lessons = send_request(token, start_date.strftime("%Y-%m-%d"),
                               end_date.strftime("%Y-%m-%d"))

        print_to_csv(lessons)
        print(f"Attendence written to {FILENAME}.")
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Exiting.")
    except error.URLError as err:
        print(f"Network error: {err}")
    except ValueError as err:
        print(f"Input error: {err}")
    except Exception as err:
        print(f"Unexpected error: {str(err)}")


if __name__ == "__main__":
    main()
