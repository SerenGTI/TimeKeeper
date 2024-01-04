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

To view the current week, use
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

