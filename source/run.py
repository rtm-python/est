# -*- coding: utf-8 -*-

"""
Main module to run application.
"""
import sys
sys.path.append('source')

# Application modules import
from blueprints import application
from models import database
from identica import telegram as bot

bot.init(False)

if __name__ == '__main__':
#	bot.run()
	application.run('0.0.0.0')
	bot.stop()
