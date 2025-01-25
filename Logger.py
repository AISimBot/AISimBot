import logging
import pytz
from datetime import datetime

class TimeZoneFormatter(logging.Formatter):
    """Custom logging formatter to display time in the specified time zone."""
    def __init__(self, fmt=None,             style=None, datefmt=None, timezone='UTC'):
        super().__init__(fmt, datefmt, style=style)
        self.timezone = pytz.timezone(timezone)

    def converter(self, timestamp):
        # Convert timestamp to datetime object in UTC
        dt = datetime.utcfromtimestamp(timestamp)
        # Convert UTC datetime to the specified time zone
        return pytz.utc.localize(dt).astimezone(self.timezone)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()

def get_logger(timezone='UTC'):
    """
    Create a custom logger with timestamps in the specified time zone.
    :param timezone: str, time zone name (e.g., 'US/Eastern')
    :return: logging.Logger
    """
    log = logging.getLogger(__name__)
    if not log.hasHandlers():  # Avoid adding handlers multiple times
        log.setLevel(logging.INFO)

        # Define a formatter with time in the specified time zone
        formatter = TimeZoneFormatter(
            fmt="{asctime}\t{levelname}\t{module}\t{threadName}\t{funcName}\t{lineno}\n{message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S %Z",
            timezone=timezone
        )

        file_handler = logging.FileHandler("log.txt", mode="a", encoding="utf-8")
        console_handler = logging.StreamHandler()

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        log.addHandler(file_handler)
        log.addHandler(console_handler)

    return log
