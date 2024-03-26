# TODO use logging, log formatting (file/func/line for error, etc.)

import sys

DEBUG_LOGGING = True


def warn(msg):
    sys.stderr.write(f'WARNING: {msg}\n')


def error(msg):
    sys.stderr.write(f'ERROR: {msg}\n')


def debug(msg):
    if DEBUG_LOGGING:
        sys.stderr.write(f'DEBUG: {msg}\n')
