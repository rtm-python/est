# -*- coding: utf-8 -*-

"""
Configuration module to define all application variables and constants.
"""

# Standard libraries import
import os
import sys
import json
import logging
from enum import Enum

# Environment values
CONFIG_PATH_KEY = 'EST_CONFIG_PATH'
LOCALE_PATH_KEY = 'EST_LOCALE_PATH'

# Application constants
CONFIG_PATH = 'config/app.json'
LOCALE_PATH = 'source/locale.json'
PLUGIN_LIST = [
	'arithmetic',
	'word2word',
	'image2word'
]

# Initiate configuration
try:
	if not os.path.isfile(os.environ.get(CONFIG_PATH_KEY, CONFIG_PATH)):
		raise ValueError('Configuration file undefined!')
	with open(os.environ.get(CONFIG_PATH_KEY, CONFIG_PATH), 'r') as config_file:
		config = json.load(config_file)
except Exception as exc:
	logging.error(getattr(exc, 'message', repr(exc)))
	sys.exit(0)

# Initiate localization
try:
	if not os.path.isfile(os.environ.get(LOCALE_PATH_KEY, LOCALE_PATH)):
		raise ValueError('Localization file undefined!')
	with open(os.environ.get(LOCALE_PATH_KEY, LOCALE_PATH), 'r') as locale_file:
		locale = json.load(locale_file)
except Exception as exc:
	logging.error(getattr(exc, 'message', repr(exc)))
	sys.exit(0)

# Initiate logging
if config.get('logging'):
	logging.basicConfig(
		format=config['logging'].get('format'),
		level=config['logging'].get('level')
	)


class UrlPrefix(Enum):
	"""
	Application url_prefix enumeration.
	"""
	base = '/'
	cabinet = '/cabinet/'
	results = '/results/'
	examination = '/examination/'
