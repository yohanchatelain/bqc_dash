import colorlog
import logging
import os


debug_color = os.getenv("BQC_DEBUG_COLOR", "0") == "1"

# Create a logger
std_logger = logging.getLogger("BQC-dash")
std_logger.setLevel(logging.DEBUG)

# Create a file handler to log messages to a file
file_handler = logging.FileHandler("bqc.log")
file_handler.setLevel(logging.DEBUG)

# Create a console handler to log messages to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Date format
datefmt = "%Y-%m-%d %H:%M:%S"

# Define a logging format
format = "%(name)s> [%(asctime)s] %(levelname)s: %(message)s"
formatter = logging.Formatter(format, datefmt=datefmt)
file_handler.setFormatter(formatter)

colorformat = (
    "%(name)s> %(funcName)s:%(lineno)d| %(log_color)s%(levelname)s: %(message)s"
)
colorformatter = colorlog.ColoredFormatter(colorformat, datefmt=datefmt)
console_handler.setFormatter(colorformatter)

# Set logger-level to QCVISU_LOGGER_LEVEL
logger_level = os.getenv("BQC_LOGGER_LEVEL", "INFO").upper()
print(f"Logger level: {logger_level}")
if logger_level == "DEBUG":
    print("Logger level: DEBUG")
    console_handler.setLevel(logging.DEBUG)
elif logger_level == "INFO":
    console_handler.setLevel(logging.INFO)
elif logger_level == "WARNING":
    console_handler.setLevel(logging.WARNING)
elif logger_level == "ERROR":
    console_handler.setLevel(logging.ERROR)
elif logger_level == "CRITICAL":
    console_handler.setLevel(logging.CRITICAL)


# Add handlers to the logger
std_logger.addHandler(file_handler)
std_logger.addHandler(console_handler)


def set_logger_level(level):
    """Set the logger level"""
    std_logger.setLevel(level)
    console_handler.setLevel(level)


# Logger based on icecream
from icecream import IceCreamDebugger


class IcecreamLoggerFactory:
    def __init__(self, level):
        self.ic = IceCreamDebugger(includeContext=True, prefix="BQC ")
        self.set_level(level)

    def set_level(self, level):
        if level == logging.DEBUG:
            self.ic.configureOutput(outputFunction=std_logger.debug)
        elif level == logging.INFO:
            self.ic.configureOutput(outputFunction=std_logger.info)
        elif level == logging.WARNING:
            self.ic.configureOutput(outputFunction=std_logger.warning)
        elif level == logging.ERROR:
            self.ic.configureOutput(outputFunction=std_logger.error)
        elif level == logging.CRITICAL:
            self.ic.configureOutput(outputFunction=std_logger.critical)

    def __call__(self, *args, **kwargs):
        self.ic(*args, **kwargs)


import traceback


class IcecreamLogger:
    def __init__(self):
        self.debug_logger = IcecreamLoggerFactory(logging.DEBUG)
        self.info_logger = IcecreamLoggerFactory(logging.INFO)
        self.warning_logger = IcecreamLoggerFactory(logging.WARNING)
        self.error_logger = IcecreamLoggerFactory(logging.ERROR)
        self.critical_logger = IcecreamLoggerFactory(logging.CRITICAL)

    def debug(self, *args, **kwargs):
        traceback.print_stack()
        self.debug_logger(*args, **kwargs)

    def info(self, *args, **kwargs):
        self.info_logger(*args, **kwargs)

    def warning(self, *args, **kwargs):
        self.warning_logger(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.error_logger(*args, **kwargs)

    def critical(self, *args, **kwargs):
        self.critical_logger(*args, **kwargs)


# logger = IcecreamLogger()
logger = std_logger
