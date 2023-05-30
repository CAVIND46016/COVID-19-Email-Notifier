import logging
import sys
import os
from settings import LOGS_DIR


class ColoredFormatter(logging.Formatter):
    blue = "\033[94m"
    green = "\033[92m"
    warning = "\033[93m"
    fail = "\033[91m"
    end = "\033[0m"
    bold = "\033[1m"
    italics = "\033[3m"
    critical = "\033[1;41m"

    def __init__(self, fmt, date_fmt):
        super().__init__()
        self.fmt = fmt
        self.date_fmt = date_fmt
        pattern = "%(levelname)s"
        _fmt = self.fmt.split(pattern)
        self.formats = {
            level: f"{self.italics}{_fmt[0]}{self.bold}{color}{pattern}{self.end}{_fmt[1]}"
            for level, color in [
                (logging.DEBUG, self.blue),
                (logging.INFO, self.green),
                (logging.WARNING, self.warning),
                (logging.ERROR, self.fail),
                (logging.CRITICAL, self.critical)
            ]
        }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.date_fmt)
        return formatter.format(record)


def get_custom_logger(**kwargs):
    logger = logging.getLogger()
    logger.setLevel(level="DEBUG")

    logger.handlers = []

    # Formatting
    fmt = kwargs.get(
        "fmt",
        "%(asctime)s - {%(filename)s:%(lineno)d} - %(funcName)s - %(levelname)s - %(message)s"
    )
    date_fmt = kwargs.get(
        "datefmt", "%Y-%m-%d %H:%M:%S"
    )
    formatter = logging.Formatter(fmt, date_fmt)

    # Stream Handler
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(level=kwargs.get("level", "INFO"))
    if kwargs.get("stream_fmt") == "color":
        stream_handler.setFormatter(ColoredFormatter(fmt, date_fmt))
    else:
        stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # RotatingFileHandler
    filename = kwargs.get("filename")
    if filename:
        filename = os.path.join(LOGS_DIR, os.path.basename(filename))
        file_handler = logging.FileHandler(
            filename,
            mode=kwargs.get("mode", "a"),
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(
            level=kwargs.get("file_handler_level", "DEBUG")
        )
        logger.addHandler(file_handler)

    return logger
