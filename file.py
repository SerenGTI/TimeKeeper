

import re
import datetime as dt
import holidays

from log import *

work_per_week = dt.timedelta(hours=39, minutes=30)
work_per_day = work_per_week / 5


def same_day(rhs: dt.datetime, lhs: dt.datetime) -> bool:
    return rhs.day == lhs.day and rhs.month == lhs.month and rhs.year == lhs.year

class Entry:
    # 2023-01-03 13:30 - 18:00
    _entry_date = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")
    _entry_times = re.compile(".{10} (.{5})( - (.{5}))?")
    # 2023-01-03 V
    _entry_vacation = re.compile(".{10} V")

    date = None
    start = None
    end = None
    vacation = False

    def __init__(self, line: str):
        # Try to find the date of the entry
        date_str = self._entry_date.match(line).group()
        date = dt.date.fromisoformat(date_str)
        self.date = date

        if self._entry_vacation.match(line):
            # found vacation
            self.vacation = True
            return

        times = self._entry_times.match(line)
        start_time = dt.time.fromisoformat(times.group(1))
        self.start = dt.datetime(year=date.year, month=date.month, day=date.day, hour=start_time.hour, minute=start_time.minute)

        end_time = times.group(3) # may be None
        if end_time == None and dt.date.today() == date:
            self.end = dt.datetime.now()
        elif end_time == None and dt.date.today() != date:
            raise ValueError(f"Could not parse {line} into a data entry.")
        else:
            end_time = dt.time.fromisoformat(end_time)
            self.end = dt.datetime(year=date.year, month=date.month, day=date.day, hour=end_time.hour, minute=end_time.minute)

    def duration(self, reference=None) -> dt.timedelta:
        if reference == None:
            if self.end == None:
                reference = dt.datetime.now()
            else:
                reference = self.end
        return reference - self.start

    def __str__(self):
        # TODO: work sessions spanning across day boundaries are not registered correctly
        output = ":".join(str(self.start).split(":")[:-1])
        if self.end != None:
            output += " - " + ":".join(str(self.end).split(":")[:-1]).split(" ")[1]
        return output

    def duration_str(self, reference=None):
        dur = self.duration(reference)
        return ":".join(str(dur).split(":")[:-1])

    def is_vacation(self) -> bool:
        return self.vacation



class DataFile:
    # 2023-01-03 13:30 - 18:00
    entry_date = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")
    entry_times = re.compile(".{10} (.{5})( - (.{5}))?")

    work_times = {}
    vacation = {}

    start_date = None
    local_holidays = None

    # fallback country and region
    _country = "US"
    _region = None

    # File stuff
    _filename = "local.tkpdata"


    def __init__(self):
        with open(self._filename, "r") as file:
            for l in file:
                if l == "\n":
                    continue # skip empty lines

                if l[0] == "$":
                    self.loadMetaData(l)
                    continue
                if l[0] == "#":
                    # ignore comments
                    continue

                day = Entry(l)

                if day.is_vacation():
                    self.vacation[day.date] = True
                    continue

                try:
                    self.work_times[day.date] += day.duration()
                except KeyError:
                    self.work_times[day.date] = day.duration()

        self.local_holidays = holidays.country_holidays(self.country, subdiv=self.region)

    def loadMetaData(self, line: str):
        line = line[1:-1] # discard $ at the beginning and \n at the end
        a = line.split("=")
        if a[0] == "start":
            self.start_date = dt.date.fromisoformat(a[1])
        elif a[0] == "country":
            self.country = a[1]
        elif a[0] == "region":
            self.region = a[1]
        else:
            print(f"Ignoring unknown meta data config flag '{a[0]}'")

    def getExpected(self, date: dt.date) -> dt.timedelta:
        if self.isVacation(date):
            return dt.timedelta(0)
        if date.weekday() >= 5:
            # saturday or sunday
            return dt.timedelta(0)
        return work_per_day if self.isInWorkTime(date) else dt.timedelta(0)

    def getActual(self, date: dt.date) -> dt.timedelta:
        duration = dt.timedelta(0)
        if self.isHoliday(date) and date.weekday() < 5 and (self.start_date == None or self.start_date <= date): # holiday work day
            duration += work_per_day

        # get work times from database
        try:
            duration += self.work_times[date]
        except KeyError:
            pass
        return duration

    def isHoliday(self, date: dt.date) -> bool:
        return date in self.local_holidays

    def isInWorkTime(self, date: dt.date) -> bool:
        if self.start_date == None:
            return True # we don't know when to start

        if date < self.start_date:
            return False
        return True

    def isVacation(self, date: dt.date) -> bool:
        return date in self.vacation

    def startTracking(self):
        with open(self._filename, "a+") as file:
            file.seek(0)
            for l in file:
                if l == "\n":
                    continue # skip empty lines
                if not l[0] in ["$", "#"]:
                    # Not a special line
                    if len(l) <= 17:
                        entry = Entry(l)
                        warn(f"You already started working at {str(entry).split(' - ')[0]}. ({entry.duration_str()}h ago)")
                        return

            new_line = ":".join(str(dt.datetime.now()).split(":")[:-1])
            file.write(new_line + "\n")
        print("You are now working.")

    def stopTracking(self):
        start_found = False
        entry = None

        file_str = ""
        with open(self._filename, "r") as file:
            # file.seek(0)
            for l in file:
                if l == "\n":
                    file_str += l; # skip empty lines
                    continue
                if not l[0] in ["$", "#"]:
                    # Not a special line
                    if len(l) <= 17:
                        if start_found:
                            error("There are multiple unfinished work sessions. Did not modify file.")
                            return
                        entry = Entry(l)
                        entry.end = dt.datetime.now()
                        if not same_day(entry.start, entry.end):
                            error("The current work session did not start today. Did not modify file.")
                        start_found = True
                        file_str += str(entry) + "\n";

                    else:
                        file_str += l;
                else:
                    file_str += l;

        if not start_found:
            error("You never started working.")
            return

        print("You stopped working.")
        print(f"{entry}. This session was {entry.duration_str()}h long.")

        with open(self._filename, "w") as file:
            file.write(file_str)

