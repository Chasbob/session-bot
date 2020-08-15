import os
import sys
import logging
import datetime

CONSOLE_LEVEL = logging.DEBUG
FILE_LEVEL = logging.INFO

def init():
    logging.addLevelName(logging.WARNING, 'WARN')
    logging.addLevelName(logging.CRITICAL, 'FATAL')
    logger = logging.getLogger('session-bot')
    logger.setLevel(logging.DEBUG)

    console_format = logging.Formatter('%(levelname)5s %(module)6s: %(message)s')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_format)
    console_handler.setLevel(CONSOLE_LEVEL)

    logger.addHandler(console_handler)

def fatal_error(*args, **kwargs):
    logger = logging.getLogger('session-bot')
    logger.critical(*args, **kwargs)
    sys.exit(1)
