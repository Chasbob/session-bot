import sys
import json
import logging
import os

from .log import fatal_error

logger = logging.getLogger('session-bot')

CONFIG = os.getenv('CONFIG')

def init():
    global config
    logger.info('Loading config...')

    try:
        if CONFIG[0] == '{':
            config = json.loads(CONFIG)
        else:
            with open(CONFIG) as file:
                try:
                    config = json.load(file)
                except json.decoder.JSONDecodeError:
                    fatal_error(f"↳ Cannot parse '{CONFIG}'")

    except OSError:
        fatal_error(f"↳ Cannot load '{CONFIG}'")
