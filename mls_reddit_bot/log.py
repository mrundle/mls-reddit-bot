# TODO use logging, log formatting (file/func/line for error, etc.)

import sys

DEBUG_LOGGING = True

def _log(lvl, msg):
    sys.stderr.write(f'{lvl.upper()}: {msg}\n')

def error(msg):
    _log('ERROR', msg)

def warn(msg):
    _log('WARNING', msg)

def info(msg):
    _log('INFO', msg)

def debug(msg):
    if DEBUG_LOGGING:
        _log('DEBUG', msg)
