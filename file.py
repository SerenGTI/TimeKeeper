

import re
import datetime as dt

work_per_week = dt.timedelta(hours=39, minutes=30)


class DataFile:
    # 2023-01-03 13:30 - 18:00
    entry_date = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")
    entry_times = re.compile(".{10} (.{5})( - (.{5}))?")

    work_times = {}

    def __init__(self):
        with open("local.tkpdata") as file:
            for l in file:
                if l == "\n":
                    continue # skip empty lines

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

    def get(self, date: dt.date) -> dt.timedelta:
        try:
            time = self.work_times[date]
            return time
        except KeyError:
            return dt.timedelta(0)






