#!/usr/bin/env python3

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


def send_request(token: str,
                 start: str,
                 end: str,
                 url: str = URL,
                 params: dict[str, typing.Any] = PARAMS) -> None:
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

    with opener.open(new_url) as response:
        content = response.read().decode("utf-8", errors="replace")
        parsed_data = json.loads(content)
        for elem in parsed_data:
            print(elem["Tantargy"])


def get_weeks_in_month(
        year: int,
        month: int) -> list[tuple[datetime.datetime, datetime.datetime]]:
    start_date = datetime.datetime(year, month, 1)

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    end_date = datetime.datetime(next_year, next_month,
                                 1) - datetime.timedelta(days=1)

    current_weekday = start_date.weekday()
    days_until_monday = (7 - current_weekday) % 7
    first_monday = start_date + datetime.timedelta(days=days_until_monday)

    weeks = []
    week_start = first_monday
    while week_start <= end_date:
        week_end = week_start + datetime.timedelta(days=5)

        if week_end > end_date:
            week_end = end_date

        weeks.append((week_start, week_end))
        week_start += datetime.timedelta(days=7)

    return weeks


def main():
    try:
        if len(sys.argv) != 3:
            raise ValueError(
                "Usage: python3 create_attendence.py <YEAR> <MONTH>")

        year = int(sys.argv[1])
        month = int(sys.argv[2])
        weeks_in_month = get_weeks_in_month(year, month)

        show_guide()
        token = read_token()

        for start, end in weeks_in_month:
            send_request(token, start.strftime("%Y-%m-%d"),
                         end.strftime("%Y-%m-%d"))
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
