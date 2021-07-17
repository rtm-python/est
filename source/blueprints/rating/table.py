# -*- coding: utf-8 -*-

"""
Blueprint module to handle scoreboard chart routes.
"""

# Standard libraries import
import sys
import json
import datetime
import importlib
import logging

# Application modules import
from blueprints import application
from blueprints.rating import blueprint
from blueprints.__locale__ import __
from models.process_store import ProcessStore
from models.test_store import TestStore
from models.entity.process import Process
from blueprints.testing.player import get_crammers_expression
from config import EXTENSION_LIST

# Additional libraries import
from flask import render_template
from flask import redirect
from flask import session
from flask import request
from flask import url_for
from flask_login import current_user

ALL_PERIODS = 'all-days'
PERIODS = ['30-days', '7-days', 'today']
ALL_EXTENSIONS = 'all-extensions'


@blueprint.route('/top/', methods=('GET',))
@blueprint.route('/top/<period>/', methods=('GET',))
@blueprint.route('/top/<period>/<extension>/', methods=('GET',))
def get_top(period: str = ALL_PERIODS, extension: str = ALL_EXTENSIONS):
	"""
	Return top rating table page.
	"""
	if session.get('timezone_offset') is None:
		return redirect(url_for('testing.get_catalog'))
	if (period not in PERIODS and period != ALL_PERIODS) or \
			(extension not in EXTENSION_LIST and extension != ALL_EXTENSIONS):
		return redirect(url_for('rating.get_top'))
	until = datetime.datetime.utcnow() + datetime.timedelta(days=1) - \
		datetime.timedelta(minutes=session['timezone_offset'])
	until = until.replace(hour=0, minute=0, second=0, microsecond=0)
	if period == ALL_PERIODS:
		since = None
	elif period == PERIODS[0]:
		since = until - datetime.timedelta(days=30)
	elif period == PERIODS[1]:
		since = until - datetime.timedelta(days=7)
	elif period == PERIODS[2]:
		since = until - datetime.timedelta(days=1)
	top_crammers = ProcessStore.get_top_crammers(
		0, 10, None if extension == ALL_EXTENSIONS else extension,
		None, None, None, get_crammers_expression(), since, until
	)
	info_page = None
	user_crammers = None
	if not current_user.is_authenticated:
		session['anonymous-rating'] = (session.get('anonymous-rating') or 0) + 1
		if session['anonymous-rating'] > 5:
			del session['anonymous-rating']
			info_page = render_template('info/join_rating.html')
	elif current_user.get_name() is not None:
		try:
			user_crammers = ProcessStore.get_user_crammers(
				None if extension == ALL_EXTENSIONS else extension,
				None, None, current_user.get_name().uid,
				get_crammers_expression(), since, until
			)
		except:
			logging.error(getattr(exc, 'message', repr(exc)))
			logging.error(current_user.get_name().value, current_user.get_name().uid, extension)
			user_crammers = None
	return render_template(
		'rating/table.html',
		periods=[ ALL_PERIODS ] + PERIODS,
		extensions=[ ALL_EXTENSIONS ] + EXTENSION_LIST,
		current_period=period,
		current_extension=extension,
		top_crammers=top_crammers,
		subtitle='top 10',
		info_page=info_page,
		user_crammers=user_crammers
	)


@application.context_processor
def get_periods():
	"""
	Return periods.
	"""
	def _periods() -> object:
		return __periods()
	return dict(__periods=__periods)


def __periods() -> object:
	"""
	Return periods.
	"""
	return PERIODS
