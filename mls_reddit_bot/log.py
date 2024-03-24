import sys


DEBUG_LOGGING = True

def warn(msg):
    sys.stderr.write(f'WARNING: {msg}\n')


def debug(msg):
    if DEBUG_LOGGING:
        sys.stderr.write(f'DEBUG: {msg}\n')
