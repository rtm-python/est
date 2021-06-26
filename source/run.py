# -*- coding: utf-8 -*-

"""
Main module to run application.
"""

# Standard libraries import
import logging
import sys

# Append source path on wsgi initialization
sys.path.append('source')

# Application modules import
from blueprints import application
from models import database
from config import CONFIG
from plugins import PluginManager


@application.cli.command('run-identica')
def run_identica():
	"""
	Run PluginManager to communicate with application identica bot.
	"""
	logging.getLogger().level = logging.INFO
	PluginManager(
		'identica', domain_url='https://crammer.scene.kz').execute('run')


# Run application on executing module
if __name__ == '__main__':
	logging.getLogger().level = logging.DEBUG
	application.run(CONFIG['web']['host'], CONFIG['web']['port'])
