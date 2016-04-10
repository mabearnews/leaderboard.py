"""Miscelaneous helper functions"""
from datetime import datetime

def get_time_period(year=datetime.today().year, month=datetime.today().month):
    """Returns a tuple containing the first of the month and the first of the next month,
    capturing the entire month. Times are datetime objects"""

    start = datetime(year, month, 1)

    # Wrap month around to January from December
    end = datetime(year, month + 1, 1) if month < 12 else datetime(year, 1, 1)

    print(str(start) + "  " + str(end))

    return (start, end)

