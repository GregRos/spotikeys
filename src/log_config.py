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
    _format = "%(asctime)s %(name)s %(message)s"

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

    def _get_name_emoji(self, name: str):
        match name:
            case "keyboard":
                return "#️⃣ "
            case "server":
                return "⚙️ "
            case "client":
                return "🎮"
        return name

    def format(self, record):
        record.name = self._get_name_emoji(record.name)
        formatter = self.formatters[record.levelno]
        return formatter.format(record)


def setup_logging():
    init(autoreset=True)
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ch = logging.StreamHandler()
    # Set a format for the console handler
    ch.setFormatter(CustomFormatter())
    file_handler = logging.FileHandler("log.log", encoding="utf-8")
    # Add the console handler to the logger
    logging.basicConfig(handlers=[ch, file_handler], level=logging.INFO)
    logging.getLogger("server").setLevel(logging.DEBUG)
