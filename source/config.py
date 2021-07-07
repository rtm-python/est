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
EXTENSION_PATH_KEY = 'EST_EXTENSION_PATH'
INFO_TEMPLATE_PATH_KEY = 'EST_INFO_TEMPLATE_PATH'

# Application constants
CONFIG_PATH = 'config/app.json'
LOCALE_PATH = 'source/locale.json'
EXTENSION_PATH = 'source/extensions'
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

# Initiate extensions list
try:
	if not os.path.exists(os.environ.get(
			EXTENSION_PATH_KEY, EXTENSION_PATH)):
		raise ValueError('Extensions folder undefined!')
	EXTENSION_LIST = []
	for filename in os.listdir(os.environ.get(
			EXTENSION_PATH_KEY, EXTENSION_PATH)):
		if filename.endswith('.py'):
			EXTENSION_LIST += [os.path.join(filename[:len(filename) - 3])]
except Exception as exc:
	logging.error(getattr(exc, 'message', repr(exc)))
	sys.exit(0)

# Initiate extensions list
try:
	if not os.path.exists(os.environ.get(
			INFO_TEMPLATE_PATH_KEY, INFO_TEMPLATE_PATH)):
		raise ValueError('Info template folder undefined!')
	INFO_TEMPLATE_LIST = []
	for filename in os.listdir(os.environ.get(
			INFO_TEMPLATE_PATH_KEY, INFO_TEMPLATE_PATH)):
		if filename.endswith('.html'):
			INFO_TEMPLATE_LIST += [os.path.join('info', filename)]
	INFO_TEMPLATE_LIST = sorted(INFO_TEMPLATE_LIST)
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
	rating = '/rating/'
