# -*- coding=utf-8 -*-
"""Rotating log files."""
import codecs
import logging
import logging.handlers
import os
import pathlib
import time

import colorlog

from ottbot import config as config_


class DailyRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """File handler that rotates the filename daily."""

    def __init__(self, log_folder_path: str) -> None:
        """
        Rotates logs on daily basis.

        The filename of the most recent log file is `f"{time.strftime("%m-%d-%Y")}.log"`.
        """
        if not os.path.exists(log_folder_path):
            pathlib.Path(log_folder_path).mkdir(parents=True)

        self.log_folder_path = log_folder_path
        filename = os.path.join(
            self.log_folder_path, f"{self.filename}.log"
        )  # see the bottom of the file for format identifiers

        logging.handlers.TimedRotatingFileHandler.__init__(
            self, filename, when="D", interval=1, backupCount=0, encoding="utf-8"
        )
        # `when` kwarg
        # Calculate the real rollover interval, which is just the number of
        # seconds between rollovers.  Also set the filename suffix used when
        # a rollover occurs.  Current 'when' events supported:
        # S - Seconds
        # M - Minutes
        # H - Hours
        # D - Days
        # midnight - roll over at midnight
        # W{0-6} - roll over on a certain day; 0 - Monday
        #
        # Case of the 'when' specifier is not important; lower or upper case
        # will work.

    @property
    def filename(self) -> str:
        return time.strftime("%m-%d-%Y")

    def doRollover(self):
        """
        Does the file swap.

        !!! note
            You can't use the `self.setStream` method because that
            flushes the input, but the stream is closed so the flush
            errors.
        """
        self.stream.close()
        # get the time that this sequence started at and make it a TimeTuple
        # t = self.rollover_at - self.interval
        # time_tuple = time.localtime(t)
        self.base_filename = os.path.join(self.log_folder_path, f"{self.filename}.log")

        if self.encoding:
            self.stream = codecs.open(self.base_filename, "w", self.encoding)  # type: ignore
            # the `codecs` library doesn't inherit attrs correctly, it uses a `__getattr__` that bypasses inheritance
        else:
            self.stream = open(self.base_filename, "w")

        self.rolloverAt += self.interval


FMT = "%(asctime)s %(name)s %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"

color_formatter = colorlog.ColoredFormatter(
    fmt="%(log_color)s" + FMT,
    datefmt=DATE_FMT,
    reset=True,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)
formatter = logging.Formatter(fmt=FMT, datefmt=DATE_FMT)

# stdout logger uses color
logger = colorlog.getLogger("ottbot")
handler = logging.StreamHandler()
handler.setFormatter(color_formatter)
logger.addHandler(handler)

# file logger doesn't use color
file_handler = DailyRotatingFileHandler("./logs")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.setLevel(config_.FullConfig.from_env().log_level)

if __name__ == "__main__":

    logger.setLevel(colorlog.DEBUG)

    logger.debug("Hello there")
    logger.info("Hello there")
    logger.warning("Hello there")
    logger.error("Hello there")
    logger.critical("Hello there")

    time.sleep(2)

    logger.debug("Hello there")
    logger.info("Hello there")
    logger.warning("Hello there")
    logger.error("Hello there")
    logger.critical("Hello there")

"""
`time.strftime` identifiers

%a - abbreviated weekday name
%A - full weekday name
%b - abbreviated month name
%B - full month name
%c - preferred date and time representation
%C - century number (the year divided by 100, range 00 to 99)
%d - day of the month (01 to 31)
%D - same as %m/%d/%y
%e - day of the month (1 to 31)
%g - like %G, but without the century
%G - 4-digit year corresponding to the ISO week number (see %V).
%h - same as %b
%H - hour, using a 24-hour clock (00 to 23)
%I - hour, using a 12-hour clock (01 to 12)
%j - day of the year (001 to 366)
%m - month (01 to 12)
%M - minute
%n - newline character
%p - either am or pm according to the given time value
%r - time in a.m. and p.m. notation
%R - time in 24 hour notation
%S - second
%t - tab character
%T - current time, equal to %H:%M:%S
%u - weekday as a number (1 to 7), Monday=1. Warning: In Sun Solaris Sunday=1
%U - week number of the current year, starting with the first Sunday as the first day of the first week
%V - The ISO 8601 week number of the current year (01 to 53), where week 1 is the first week that has at
     least 4 days in the current year, and with Monday as the first day of the week
%W - week number of the current year, starting with the first Monday as the first day of the first week
%w - day of the week as a decimal, Sunday=0
%x - preferred date representation without the time
%X - preferred time representation without the date
%y - year without a century (range 00 to 99)
%Y - year including the century
%Z or %z - time zone or name or abbreviation
%% - a literal % character
"""
