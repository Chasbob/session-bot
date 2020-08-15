import logging

from .util import log
log.init()

from .util import config
config.init()

from .bot import bot

logger = logging.getLogger('session-bot')

def init():
	logger.info(f'Starting session-bot')
	bot.main()
