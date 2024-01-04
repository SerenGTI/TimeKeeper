

import re
import datetime as dt
import holidays

work_per_week = dt.timedelta(hours=39, minutes=30)
work_per_day = work_per_week / 5

local_holidays = holidays.country_holidays("DE", subdiv="BW")

class DataFile:
    # 2023-01-03 13:30 - 18:00
    entry_date = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")
    entry_times = re.compile(".{10} (.{5})( - (.{5}))?")

    work_times = {}

    start_date = None

    def __init__(self):
        with open("local.tkpdata") as file:
            for l in file:
                if l == "\n":
                    continue # skip empty lines

                if l[0] == "$":
                    self.loadMetaData(l)
                    continue

                # Try to find the date of the entry
                date_str = self.entry_date.match(l).group()
                date = dt.date.fromisoformat(date_str)

                times = self.entry_times.match(l)
                start_time = dt.time.fromisoformat(times.group(1))
                start = dt.datetime(year=date.year, month=date.month, day=date.day, hour=start_time.hour, minute=start_time.minute)


                end_time = times.group(3) # may be None
                if end_time == None and dt.date.today() == date:
                    end = dt.datetime.now()
                elif end_time == None and dt.date.today() != date:
                    print("Error in the file at line", l)
                    exit()
                else:
                    end_time = dt.time.fromisoformat(end_time)
                    end = dt.datetime(year=date.year, month=date.month, day=date.day, hour=end_time.hour, minute=end_time.minute)

                work_duration = end-start

                try:
                    self.work_times[date] += work_duration
                except KeyError:
                    self.work_times[date] = work_duration

    def loadMetaData(self, line: str):
        line = line[1:-1] # discard $ at the beginning and \n at the end
        a = line.split("=")
        if a[0] == "start":
            self.start_date = dt.date.fromisoformat(a[1])
        else:
            print(f"Ignoring unknown meta data config flag '{a[0]}'")

    def getExpected(self, date: dt.date) -> dt.timedelta:
        if date.weekday() >= 5:
            # saturday or sunday
            return dt.timedelta(0)
        return work_per_day if self.isInWorkTime(date) else dt.timedelta(0)

    def getActual(self, date: dt.date) -> dt.timedelta:
        duration = dt.timedelta(0)
        if date in local_holidays and date.weekday() < 5 and (self.start_date == None or self.start_date <= date): # holiday work day
            duration += work_per_day

        # get work times from database
        try:
            duration += self.work_times[date]
        except KeyError:
            pass
        return duration

    def isInWorkTime(self, date: dt.date) -> bool:
        if self.start_date == None:
            return True # we don't know when to start

        if date < self.start_date:
            return False
        return True



