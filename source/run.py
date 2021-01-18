# -*- coding: utf-8 -*-

"""
Main module to run application.
"""

# Application modules import
from blueprints import application
from models import database
from identica import telegram as bot

if __name__ == '__main__':
	bot.init(False)
	bot.run()
	application.run()
	bot.stop()
