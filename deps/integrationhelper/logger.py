"""Logger."""
import logging


class Logger:
    """Custom logger."""

    def __init__(self, name="integrationhelper"):
        self.name = name.replace("/", ".")

    def debug(self, message):
        """Info messages."""
        logging.getLogger(self.name).debug(message)

    def info(self, message):
        """Info messages."""
        logging.getLogger(self.name).info(message)

    def warning(self, message):
        """Info messages."""
        logging.getLogger(self.name).warning(message)

    def error(self, message):
        """Info messages."""
        logging.getLogger(self.name).error(message)

    def critical(self, message):
        """Info messages."""
        logging.getLogger(self.name).critical(message)
