# -*- coding: utf-8 -*-

"""
Blueprint module to handle scoreboard chart routes.
"""

# Standard libraries import
import json
import datetime
import logging
import random

# Application modules import
from blueprints import application
from blueprints.rating import blueprint
from blueprints.__locale__ import __
from models.process_store import ProcessStore
from models.entity.process import Process
from config import EXTENSION_LIST
from blueprints.test.process import get_crammers_expression

# Additional libraries import
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask_login import current_user


@blueprint.route('/chart/personal/<extension>/<criteria>/', methods=('GET',))
def get_chart(extension: str, criteria: str):
	"""
	Return personal chart page.
	"""
	criterias = ['crammers', 'passed-tests', 'correct-answers']
	if (extension not in EXTENSION_LIST and extension != 'all-extensions') or \
			criteria not in criterias:
		return redirect(
			url_for('rating.get_chart', extension='all-extensions', criteria='crammers')
		)
	until = datetime.datetime.utcnow() + datetime.timedelta(days=1)
	until = until.replace(hour=0, minute=0, second=0, microsecond=0)
	since = until - datetime.timedelta(days=30)
	chart_data = ProcessStore.get_chart_data(
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
			process_date_local in chart_data:
		if name_value is None:
			name_value = __('Anonymous User')
		name_data = data.get(name_value)
		if name_data is None:
			hex_color = '#%06X' % random.randint(0,256**3 - 1)
			name_data = {
				'value': [0] * 30,
				'bg-color': hex_color + '%02X' % 25,
				'fg-color': hex_color
			}
			data[name_value] = name_data
		if criteria == 'crammers':
			name_data['value'][date_index_dict[process_date_local]] = total
		elif criteria == 'tests':
			name_data['value'][date_index_dict[process_date_local]] = process_count
		elif criteria == 'answers':
			name_data['value'][date_index_dict[process_date_local]] = correct_count
	return render_template(
		'rating/chart.html',
		extensions=EXTENSION_LIST,
		current_extension=extension,
		criterias=criterias,
		current_criteria=criteria,
		days=days,
		data=data,
		nav_active='ratings'
	)
