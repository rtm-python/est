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
PLUGIN_PATH_KEY = 'EST_PLUGIN_PATH'
INFO_TEMPLATE_PATH_KEY = 'EST_INFO_TEMPLATE_PATH'

# Application constants
CONFIG_PATH = 'config/app.json'
LOCALE_PATH = 'source/locale.json'
PLUGIN_PATH = 'source/plugins'
INFO_TEMPLATE_PATH = 'source/templates/info'

# Initiate configuration
try:
	if not os.path.isfile(os.environ.get(CONFIG_PATH_KEY, CONFIG_PATH)):
		raise ValueError('Configuration file undefined!')
	with open(os.environ.get(CONFIG_PATH_KEY, CONFIG_PATH), 'r') as config_file:
		CONFIG = json.load(config_file)
except Exception as exc:
	logging.error(getattr(exc, 'message', repr(exc)))
	sys.exit(0)

# Initiate localization
try:
	if not os.path.isfile(os.environ.get(LOCALE_PATH_KEY, LOCALE_PATH)):
		raise ValueError('Localization file undefined!')
	with open(os.environ.get(LOCALE_PATH_KEY, LOCALE_PATH), 'r') as locale_file:
		LOCALE = json.load(locale_file)
except Exception as exc:
	logging.error(getattr(exc, 'message', repr(exc)))
	sys.exit(0)

# Initiate plugins list
try:
	if not os.path.exists(os.environ.get(
			PLUGIN_PATH_KEY, PLUGIN_PATH)):
		raise ValueError('Plugins folder undefined!')
	PLUGIN_LIST = []
	for filename in os.listdir(os.environ.get(
			PLUGIN_PATH_KEY, PLUGIN_PATH)):
		if filename.endswith('.py'):
			PLUGIN_LIST += [os.path.join(filename[:len(filename) - 3])]
except Exception as exc:
	logging.error(getattr(exc, 'message', repr(exc)))
	sys.exit(0)

# Initiate plugins list
try:
	if not os.path.exists(os.environ.get(
			INFO_TEMPLATE_PATH_KEY, INFO_TEMPLATE_PATH)):
		raise ValueError('Info template folder undefined!')
	INFO_TEMPLATE_LIST = []
	for filename in os.listdir(os.environ.get(
			INFO_TEMPLATE_PATH_KEY, INFO_TEMPLATE_PATH)):
		if filename.endswith('.html'):
			INFO_TEMPLATE_LIST += [os.path.join('info', filename)]
except Exception as exc:
	logging.error(getattr(exc, 'message', repr(exc)))
	sys.exit(0)

# Initiate logging
if CONFIG.get('logging'):
	logging.basicConfig(
		format=CONFIG['logging'].get('format'),
		level=CONFIG['logging'].get('level')
	)


class UrlPrefix(Enum):
	"""
	Application url_prefix enumeration.
	"""
	base = '/'
	test = '/test/'
	scoreboard = '/scoreboard/'
