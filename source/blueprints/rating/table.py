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
from flask import request
from flask import url_for
from flask_login import current_user


@blueprint.route('/table/top/<period>/<extension>/', methods=('GET',))
def get_top(period: str, extension: str):
	"""
	Return top rating table page.
	"""
	periods = ['30-days', '7-days', 'today']
	if (period not in periods and period != 'all-days') or \
			(extension not in EXTENSION_LIST and extension != 'all-extensions'):
		return redirect(
			url_for('rating.get_top', period='all-days', extension='all-extensions')
		)
	until = datetime.datetime.utcnow() + datetime.timedelta(days=1)
	until = until.replace(hour=0, minute=0, second=0, microsecond=0)
	if period == 'all-days':
		since = None
	elif period == periods[0]:
		since = until - datetime.timedelta(days=30)
	elif period == periods[1]:
		since = until - datetime.timedelta(days=7)
	elif period == periods[2]:
		since = until - datetime.timedelta(days=1)
	top_crammers = ProcessStore.get_top_crammers(
		0, 10, None if extension == 'all-extensions' else extension,
		None, None, None, get_crammers_expression(), since, until,
		datetime.timedelta(days=0)
	)
	all = ProcessStore.get_chart_data(
		None if extension == 'all-extensions' else extension,
		current_user.get_id(), current_user.get_token(),
		None, get_crammers_expression(), since, until,
		datetime.timedelta(days=0)
	)
	days = []
	date_index_dict = {}
	for day in range(30):
		date = until - datetime.timedelta(days=(29 - day))
		days += [	(date).strftime('%a, %d') ]
		date_index_dict[date.strftime('%Y-%m-%d')] = day
	data = {}
	for name_value, process_count, correct_count, answer_time, total, \
			process_date_local in all:
		if name_value is None:
			name_value = __('Anonumous User')
		name_data = data.get(name_value)
		if name_data is None:
			name_data = {
				'process_count': [0] * 30,
				'correct_count': [0] * 30,
				'answer_time': [0] * 30,
				'total': [0] * 30,
			}
			data[name_value] = name_data
		name_data['process_count'][date_index_dict[process_date_local]] = process_count
		name_data['correct_count'][date_index_dict[process_date_local]] = correct_count
		name_data['answer_time'][date_index_dict[process_date_local]] = answer_time
		name_data['total'][date_index_dict[process_date_local]] = total
	return render_template(
		'rating/table.html',
		periods=periods,
		extensions=EXTENSION_LIST,
		current_period=period,
		current_extension=extension,
		top_crammers=top_crammers,
		all=all,
		days=days,
		data=data,
		nav_active='ratings'
	)

"""
Result: 100%
Pass: 1 test
Count: 15 answers
Time: 30 seconds
/Difficulty/: 1.0 (for each test separatelty)

Rating = Result * Pass * Count / Time * Difficulty

(R: 100, P: 1, C: 15, T: 30)
R1 = 100 * 1 * 15 * 15 / 30 = 750

(R: 100, P: 1, C: 15, T: 45)
R1 = 100 * 1 * 15 * 15 / 45 = 500

(R: 100, P: 1, C: 5, T: 30)
R1 = 100 * 1 * 15 * 5 / 30 = 250

(R: 100, P: 1, C: 15, T: 30)
R1 = 50 * 1 * 15 * 15 / 30 = 375

[Table]
Value (R1), Pass, Count, Time  -  for each day

"""


