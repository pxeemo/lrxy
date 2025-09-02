import sys
import logging


class ColoredFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        self.use_colors = self._supports_color()

        if self.use_colors:
            self.RED = '\033[31m'
            self.YELLOW = '\033[33m'
            self.CYAN = '\033[36m'
            self.RESET = '\033[0m'
        else:
            self.RED = ''
            self.YELLOW = ''
            self.CYAN = ''
            self.RESET = ''

    def _supports_color(self):
        """Check if the terminal supports ANSI colors."""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    def format(self, record):
        if record.levelno == logging.INFO:
            return record.getMessage()
        elif record.levelno == logging.ERROR:
            record.levelname = f"{self.RED}Error{self.RESET}"
        elif record.levelno == logging.WARNING:
            record.levelname = f"{self.YELLOW}Warning{self.RESET}"
        elif record.levelno == logging.DEBUG:
            record.levelname = f"{self.CYAN}Debug{self.RESET}: {record.name}"
        return f"{record.levelname}: {record.getMessage()}"


def setup_logging(level=logging.WARNING):
    logging.basicConfig(level=level)

    logger = logging.getLogger()
    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)

    return logger


setup_logging(level=logging.WARNING)
