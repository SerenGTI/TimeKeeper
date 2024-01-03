# TimeKeeper (WIP)

A command line utility to keep track of your working hours.

## Dependencies

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

