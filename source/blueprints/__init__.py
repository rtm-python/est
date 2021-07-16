# -*- coding: utf-8 -*-

"""
Initial blueprints module to define blueprints.
"""

# Standard libraries import
import secrets
import importlib
import json

# Application modules import
from config import CONFIG
from config import UrlPrefix
from config import EXTENSION_LIST

# Additional libraries import
from flask import Flask
from flask import session
from flask import redirect
from flask import url_for
from flask_paranoid import Paranoid

# Initiate Flask object
application = Flask(
	CONFIG['name'],
	static_url_path='',
	static_folder='source/static',
	template_folder='source/template'
)
application.config['SECRET_KEY'] = CONFIG['key']
paranoid = Paranoid(application)
paranoid.redirect_view = 'base.get_home'

# Blueprint modules import and blueprints registration
# (prevent circular imports)
for module_name in \
		[
			'base',
			'testing',
			'rating'
		]:
	module = importlib.import_module('blueprints.%s' % module_name)
	application.register_blueprint(
		module.blueprint,
		url_prefix=getattr(UrlPrefix, module_name).value
	)

# Helper modules import
# (prevent circular imports)
from blueprints import __locale__


@paranoid.on_invalid_session
def redirect_on_invalid_session():
	"""
	Return redirect on invalid session.
	"""
	return redirect(url_for('base.get_home'))


@application.before_request
def make_session_permanent():
	"""
	Make all sessions permanent.
	"""
	session.permanent = True


@application.context_processor
def get_dictionary():
	"""
	Return dictionary from text string.
	"""
	def _dict(text: str) -> dict:
		return __dict(text)
	return dict(__dict=__dict)


def __dict(text: str) -> dict:
	"""
	Return dictionary from text string.
	"""
	return json.loads(text)


@application.context_processor
def get_config():
	"""
	Return configuration data by key.
	"""
	def _config(key: str) -> object:
		return __config(key)
	return dict(__config=__config)


def __config(key: str) -> object:
	"""
	Return configuration data by key.
	"""
	return CONFIG.get(key)


@application.context_processor
def get_extensions():
	"""
	Return extensions.
	"""
	def _extensions() -> object:
		return __extensions()
	return dict(__extensions=__extensions)


def __extensions() -> object:
	"""
	Return extensions.
	"""
	return EXTENSION_LIST
