# TimeKeeper (WIP)

A command line utility to keep track of your working hours.

## Dependencies

TimeKeeper automatically tracks public holidays.
As such, it requires the `holidays` package.
Install e.g., via `pip` as follows.
```bash
pip3 install holidays
```

## Usage

When you start working, simply type
```bash
tkp start
```
and when you finish, use
```bash
tkp stop
```
This will create a new entry in you work time database.
Starting when you are already working is a no-op and will instead print your current work time since the last start.
Similarly, stopping a work session when you are not working (did not issue `tkp start`) is a no-op as well.

To view your work time over longer durations, use the `view` command.
To view the current week's statistics use
```bash
tkp view
```
If you want to include more weeks, use index slicing
```bash
# current and previous week
tkp view -1:
# previous week, current week and next week
tkp view -1:1
```


## Data file

We use plain-text files to track work times because it allows simple synchronization across multiple devices via git + automatic conflict resolution.

