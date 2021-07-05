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
from blueprints.scoreboard import blueprint
from blueprints.__filter__ import FilterForm
from blueprints.__locale__ import __
from blueprints.__pagination__ import get_pagination
from blueprints.__args__ import get_string
from blueprints.__args__ import get_boolean
from blueprints.__args__ import set_value
from models.process_store import ProcessStore
from models.test_store import TestStore
from models.task_store import TaskStore
from models.entity.process import Process

# Additional libraries import
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SelectField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms import validators
from flask_login import current_user


class ChartFilterForm(FilterForm):
	"""
	This is ChartFilterForm class to retrieve form data.
	"""
	name = StringField('FilterName')
	extension = StringField('FilterExtension')
	submit = SubmitField('FilterSubmit')

	def __init__(self) -> 'ChartFilterForm':
		"""
		Initiate object with values from request
		"""
		super(ChartFilterForm, self).__init__('chart')


@blueprint.route('/chart/', methods=('GET', 'POST'))
def get_chart():
	"""
	Return scoreboard chart page.
	"""
	# Handle filter form
	filter = ChartFilterForm()
	if filter.is_submit(filter.submit.label.text) and \
			filter.validate_on_submit(): # Valid post request
		filter.store_fields()
		return redirect(filter.url_for_with_fields('scoreboard.get_chart'))
	filter.define_fields()
	name = current_user.get_name()
	# Prepare list data
	pagination = get_pagination(
		'chart',
		ProcessStore.count_charts(
			filter.name.data,
			filter.extension.data,
			current_user.get_id(),
			current_user.get_token(),
			name.uid if name is not None else None
		)
	)
	pagination['endpoint'] = 'scoreboard.get_chart'
	pagination['prefix'] = 'chart'
	charts = ProcessStore.read_charts(
		(pagination['page_index'] - 1) * pagination['per_page'],
		pagination['per_page'],
		filter.name.data,
		filter.extension.data,
		current_user.get_id(),
		current_user.get_token(),
		name.uid if name is not None else None
	)
	return render_template(
		'scoreboard/chart.html',
		filter=filter,
		charts=charts,
		pagination=pagination,
		nav_active='scoreboard'
	)
