import sys
import logging

class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno >= logging.ERROR:
            self._style._fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
        else:
            self._style._fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        return super().format(record)

def setup_logger(debug=False):
    logging.getLogger().handlers.clear()
    handler = logging.StreamHandler() # defaults to stderr
    handler.setFormatter(CustomFormatter())
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.addHandler(handler)

def error(msg):
    logging.error(msg)

def exception(msg):
    logging.exception(msg)

def warn(msg):
    logging.warning(msg)

def info(msg):
    logging.info(msg)

def debug(msg):
    logging.debug(msg)
