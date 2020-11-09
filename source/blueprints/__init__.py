# -*- coding: utf-8 -*-

"""
Initial blueprints module to define blueprints.
"""

# Standard libraries import
import secrets
import importlib

# Application modules import
from config import config
from config import locale
from config import UrlPrefix

# Additional libraries import
from flask import Flask
from flask import redirect
from flask import request
from flask import url_for
from flask import session
from flask_paranoid import Paranoid

# Initiate Flask object
application = Flask(config['name'])
application.config['SECRET_KEY'] = secrets.token_hex(256)
paranoid = Paranoid(application)
paranoid.redirect_view = 'base.landing'

# Blueprint modules import and blueprints registration
# (prevent circular imports)
for module_name in \
		[
			'base',
			'statistics',
			'examination'
		]:
	module = importlib.import_module('blueprints.%s' % module_name)
	application.register_blueprint(
		module.blueprint,
		url_prefix=getattr(UrlPrefix, module_name).value
	)


@paranoid.on_invalid_session
def redirect_on_invalid_session():
	"""
	Return redirect on invalid session.
	"""
	return redirect(url_for('base.landing'))


@application.before_request
def set_session_language():
	"""
	Set session language from client request.
	"""
	session['language'] = request.accept_languages.best_match(
		locale['__']['supported_languages']
	)


@application.context_processor
def get_localized():
	"""
	Return localized text string.
	"""
	def _(key: str) -> str:
		return __(key)
	return dict(__=__)


def __(key: str) -> str:
	"""
	Return matching by key localized text string.
	"""
	value = locale.get(key)
	if value:
		localized = value.get(session['language'])
		if localized:
			return localized
	return key
