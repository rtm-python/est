# -*- coding: utf-8 -*-

"""
Helper module to handle localization.
"""

# Standard libraries import


# Application modules import
from config import LOCALE
from blueprints import application

# Additional libraries import
from flask import request
from flask import url_for
from flask import session


@application.before_request
def set_session_language():
	"""
	Set session language from client request.
	"""
	session['language'] = request.accept_languages.best_match(
		LOCALE['__']['supported_languages']
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
	value = LOCALE.get(key)
	if value:
		localized = value.get(session['language'])
		if localized:
			return localized
	return key
