import re


def parse_year_month_str(year_month: str):
    match = re.search("(\d{4}).{1}(\d{1,2})", year_month)
    year, month = int(match.group(1)), int(match.group(2))
    return year, month
