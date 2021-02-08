# -*- coding: utf-8 -*-

"""
Blueprint module to handle test process routes.
"""

# Standard libraries import
import sys
import json
import datetime
import importlib
import logging

# Application modules import
from blueprints import application
from blueprints.test import blueprint
from blueprints.__paginator__ import get_pagination
from blueprints.__args__ import get_string
from blueprints.__args__ import get_boolean
from blueprints.__args__ import set_value
from blueprints.__alert__ import AlertType
from blueprints.__alert__ import AlertButton
from blueprints.__alert__ import Alert
from models.process_store import ProcessStore
from models.test_store import TestStore
from models.task_store import TaskStore
from models.entity.process import Process
from models.entity.examination import Examination

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


class FilterForm(FlaskForm):
	"""
	This is FilterForm class to retrieve form data.
	"""
	name = StringField('filterName')
	plugin = StringField('filterPlugin')
	hide_completed = BooleanField('filterHideCompleted')
	submit = SubmitField('filterSubmit')

	def __init__(self) -> 'FilterForm':
		"""
		Initiate object with values from request
		"""
		super(FilterForm, self).__init__()
		for field in self:
			if field.name != 'csrf_token':
				field.data = request.form.get(field.label.text)

	def define_fields(self) -> None:
		"""
		Set form fields to values from request.
		"""
		if not get_boolean('filterReset'):
			self.name.data = get_string('filterName')
			self.plugin.data = get_string('filterPlugin')
			self.hide_completed.data = get_boolean('filterHideCompleted')
		else:
			set_value('filterName', None)
			set_value('filterPlugin', None)
			set_value('filterHideCompleted', None)

	def store_fields(self) -> None:
		"""
		Set form fields to values from request.
		"""
		set_value('filterName', self.name.data)
		set_value('filterPlugin', self.plugin.data)
		set_value('filterHideCompleted', self.hide_completed.data)

	def url_for_with_fields(self, endpoint: str) -> object:
		"""
		Return url_for with defined form fields
		"""
		return url_for(
			endpoint,
			filterName=self.name.data,
			filterPlugin=self.plugin.data,
			filterHideCompleted=self.hide_completed.data
		)


class PlayerForm(FlaskForm):
	"""
	This is a PlayerForm class to retrieve form data.
	"""
	answer = StringField(validators=[validators.DataRequired()])
	submit = SubmitField()


def verify_process_owner(process: Process) -> bool:
	"""
	Return True when current_user is the process owner,
	otherwise return False.
	"""
	if process is None:
		return False
	return True
	if current_user.get_id() is not None and \
			current_user.get_id() != process.user_uid:
		return False
	if current_user.get_token() is not None and \
			current_user.get_token() != process.anonymous_token:
		return False
	return True


@blueprint.route('/process/', methods=('GET', 'POST'))
def get_process():
	"""
	Return test process page.
	"""
	# Handle filter form
	filter = FilterForm()
	if request.form.get('filterSubmit') and \
			filter.validate_on_submit(): # Valid post request
		filter.store_fields()
		return redirect(filter.url_for_with_fields('test.get_process'))
	filter.define_fields()
	# Prepare list data
	pagination = get_pagination(
		ProcessStore.count_list(
			filter.name.data,
			filter.plugin.data,
			filter.hide_completed.data,
			current_user.get_id(),
			current_user.get_token()
		)
	)
	pagination['endpoint'] = 'test.get_process'
	processes = ProcessStore.read_list(
		(pagination['page_index'] - 1) * pagination['per_page'],
		pagination['per_page'],
		filter.name.data,
		filter.plugin.data,
		filter.hide_completed.data,
		current_user.get_id(),
		current_user.get_token()
	)
	return render_template(
		'test/process.html',
		filter=filter,
		processes=processes,
		pagination=pagination,
		nav_active='test'
	)


@blueprint.route('/process/start/<uid>/', methods=('GET',))
def start(uid: str):
	"""
	Initiate test process and redirect to test process play page.
	"""
	test = TestStore.read(uid)
	if test is None:
		return redirect(url_for('test.get_process'))
	process = ProcessStore.create(
		test.id, current_user.get_id(), current_user.get_token()
	)
	return redirect(url_for('test.play', uid=process.uid))


@blueprint.route('/process/<uid>/play/', methods=('GET', 'POST'))
def play(uid: str):
	"""
	Return test process play page.
	"""
	process, test = ProcessStore.read_with_test(uid)
	if not verify_process_owner(process):
		return redirect(url_for('test.get_process'))
	if process.result is not None:
		return redirect(url_for('test.get_result', uid=uid))
	# Import plugin module and get data
	plugin_module = importlib.import_module('plugins.%s' % test.plugin)
	data = plugin_module.get_data(json.loads(test.plugin_options))
	# Read previous tasks
	task = None
	passed_tasks = TaskStore.read_list(
		offset=0, limit=0, filter_process_id=process.id)
	if passed_tasks and passed_tasks[0].answer is None:
		# Continue on existing task
		task = passed_tasks[0]
		passed_tasks = passed_tasks[1:]
	# Handle filter form
	player = PlayerForm()
	if player.validate_on_submit():
		user_answer = player.answer.data.strip()
		validation_errors = plugin_module.validate_answer(user_answer)
		if not validation_errors: # Plugin should validate anwser
			task = TaskStore.set_answer(task.uid, user_answer)
			process = ProcessStore.add_answer(process.uid, task)
			if process.result is not None:
				return redirect(url_for('test.get_result', uid=uid))
			passed_tasks = [task] + passed_tasks
			task = TaskStore.create(process.id, json.dumps(data))
			player.answer.data = None
		else:
			task = TaskStore.update(
				task.uid, process.id, json.dumps(data), None, None)
			player.answer.errors = validation_errors
	elif task is None:
		task = TaskStore.create(process.id, json.dumps(data))
	else:
		task = TaskStore.update(
			task.uid, process.id, json.dumps(data), None, None)
	return render_template(
		'test/player.html',
		process=process,
		test=test,
		data=data,
		passed_tasks=passed_tasks,
		player=player,
		nav_active='test'
	)


@blueprint.route('/process/<uid>/result/', methods=('GET',))
def get_result(uid: str):
	"""
	Return test process result page.
	"""
	process, test = ProcessStore.read_with_test(uid)
	if not verify_process_owner(process):
		return redirect(url_for('test.get_process', uid=uid))
	if process.result is None:
		return redirect(url_for('test.play'))
	# Read previous tasks
	passed_tasks = TaskStore.read_list(
		offset=0, limit=0, filter_process_id=process.id)
	return render_template(
		'test/result.html',
		process=process,
		test=test,
		passed_tasks=passed_tasks,
		nav_active='test'
	)
