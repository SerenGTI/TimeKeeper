
import sys
import calendar
import datetime as dt
import re

from typing import List, Optional, Union

from terminal import *
from file import *


def get_month_abbr_len() -> int:
    """Calculate the number of characters we need to display the month
    abbreviated name. It depends on the locale.
    """
    return max(len(calendar.month_abbr[i]) for i in range(1, 13)) + 1

def week_number(date: dt.date) -> int:
    """return iso week number for dt.date object
    :param date: date
    :return: weeknumber
    """
    return dt.date.isocalendar(date)[1]

def timedelta_format(td: dt.timedelta) -> str:
    seconds = td.total_seconds()
    minutes = seconds / 60
    hours = int(minutes / 60)
    minutes = int(minutes - (hours * 60))
    return str(hours).rjust(2) + "h " + str(minutes).rjust(2) + "min"

def str_week(
    week: List[dt.date],
    month: int,
    today: dt.date,
    data,
    locale=None,
) -> str:
    # strweek = str(week_number(week[1])).rjust(3) + ":  "
    strweek = ""

    week_sum = dt.timedelta(0)
    week_sum_expected = dt.timedelta(0)

    for day in week:
        if(day.month != month):
            strweek += "   "
            continue

        week_sum += data.getActual(day)
        week_sum_expected += data.getExpected(day)

        bg = None
        fg = None
        if day.weekday() >= 5:
            # saturday or sunday
            fg = 'dark blue'
        if day in local_holidays:
            # holidays are red (and have priority over sat/sun)
            fg = "light red"
        if not data.isInWorkTime(day):
            # if the day is before the begin of the work contract -> gray
            fg = "dark gray"

        # apply colors
        day_str = colored(str(day.day).rjust(2), fg, bg)

        # if today, reverse the colors
        if day == today:
            day_str = reverse(day_str) # custom styling for today

        # one space between days
        strweek += day_str + ' '

    if week_sum_expected == dt.timedelta(0):
        # if no work is expected in this week, hide the time overview
        pass
    else:
        completeness = f"{week_sum / week_sum_expected * 100:.0f}".rjust(3)
        # strweek += "  " + timedelta_format(week_sum) + " / " + timedelta_format(work_per_week) + f" ({completeness}%)"
        strweek += "  " + timedelta_format(week_sum) + f" ({completeness}%)"

    return strweek


def str_vertical_month(
    start: dt.date,
    end: dt.date
) -> str:
    # first week day = 0 = monday
    cal = calendar.Calendar(0)
    month_abbr_len = get_month_abbr_len()

    # load stored data
    data = DataFile()

    out = []
    header = " " * month_abbr_len + calendar.weekheader(2)
    out.append(header)

    today = dt.date.today()

    month = start.month
    new_month = True
    while start <= end:
        year = start.year

        for week in cal.monthdatescalendar(year, month):
            if not start in week:
                continue
            week_str = str_week(week, month, today, data=data)

            if new_month:
                mon_str = calendar.month_abbr[month].ljust(month_abbr_len)
                new_month = False
            else:
                mon_str = " " * month_abbr_len
            line = bold(mon_str) + week_str

            out.append(line)

        start += dt.timedelta(days=7)
        if month != start.month:
            new_month = True
        month = start.month
    return "\n".join(out)


def main():
    today = dt.date.today()

    start = today
    end = today

    if len(sys.argv) >= 2:
        regex = re.compile("(-?[0-9]+)?:(-?[0-9]+)?")
        matcher = regex.match(sys.argv[1])
        if matcher != None:
            if matcher.group(1) != None:
                # offset the start by the number of weeks
                start = start + dt.timedelta(days=7*int(matcher.group(1)))

            if matcher.group(2) != None:
                # offset the end by the number of weeks
                end = end + dt.timedelta(days=7*int(matcher.group(2)))

    print(str_vertical_month(start, end))


if __name__ == '__main__':
    main()
