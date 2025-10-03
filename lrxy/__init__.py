import sys
import logging


class ColoredFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        self.use_colors = self._supports_color()

        if self.use_colors:
            self.red = '\033[31m'
            self.yellow = '\033[33m'
            self.cyan = '\033[36m'
            self.reset = '\033[0m'
        else:
            self.red = ''
            self.yellow = ''
            self.cyan = ''
            self.reset = ''

    def _supports_color(self):
        """Check if the terminal supports ANSI colors."""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    def format(self, record):
        if record.levelno == logging.INFO:
            return record.getMessage()
        elif record.levelno == logging.ERROR:
            record.levelname = f"{self.red}Error{self.reset}"
        elif record.levelno == logging.WARNING:
            record.levelname = f"{self.yellow}Warning{self.reset}"
        elif record.levelno == logging.DEBUG:
            record.levelname = f"{self.cyan}Debug{self.reset}: {record.name}"

        msg_lines = record.getMessage().splitlines()
        ansi_length = 7 if self.use_colors else 0
        msg_start_pad = " " * (len(record.levelname) - ansi_length)
        msg = str("\n" + msg_start_pad).join(msg_lines)
        return f"{record.levelname}: {msg}"


def setup_logging(level=logging.WARNING):
    logging.basicConfig(level=level)

    logger = logging.getLogger()
    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)

    return logger


setup_logging(level=logging.WARNING)
