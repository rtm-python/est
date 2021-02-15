# -*- coding: utf-8 -*-

"""
Main module to run application.
"""

# Standard libraries import
import logging
import sys

sys.path.append('source')

# Application modules import
from blueprints import application
from models import database
from identica import telegram as bot

try:
	bot.init(False)
except:
	logging.error('Bot initialization error', exc_info=1)

if __name__ == '__main__':
	bot.run()
	application.run('0.0.0.0')
	bot.stop()
