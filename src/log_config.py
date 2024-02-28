import ctypes
import logging

from colorama import Fore, Style, init


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = Style.DIM + Fore.WHITE
    yellow = Fore.YELLOW
    red = Fore.RED
    green = Fore.GREEN
    bold_red = Style.BRIGHT + Fore.RED
    reset = Style.RESET_ALL
    _format = "[%(asctime)s] |%(levelname)s| %(name)s – %(message)s"

    @staticmethod
    def get_formatter(string: str):
        return logging.Formatter(
            string,
            datefmt="%H:%M:%S",
        )

    formatters: dict[int, logging.Formatter] = {
        logging.DEBUG: get_formatter(f"{grey}{_format}{reset}"),
        logging.INFO: get_formatter(f"{green}{_format}{reset}"),
        logging.WARNING: get_formatter(f"{yellow}{_format}{reset}"),
        logging.ERROR: get_formatter(f"{red}{_format}{reset}"),
        logging.CRITICAL: get_formatter(f"{bold_red}{_format}{reset}"),
    }

    def format(self, record):
        formatter = self.formatters[record.levelno]
        return formatter.format(record)


def setup_logging():
    init(autoreset=True)
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ch = logging.StreamHandler()
    # Set a format for the console handler
    ch.setFormatter(CustomFormatter())

    # Add the console handler to the logger
    logging.basicConfig(handlers=[ch], level=logging.INFO)
