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
from plugins.identica import Plugin as IdenticaPlugin

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

# Global constants
process_template = __('TEST') + ': %s\n' + __('STATUS') + ': %s'


class ProcessFilterForm(FilterForm):
	"""
	This is ProcessFilterForm class to retrieve form data.
	"""
	name = StringField('filterName')
	extension = StringField('filterExtension')
	hide_completed = BooleanField('filterHideCompleted')
	submit = SubmitField('filterSubmit')

	def __init__(self) -> 'ProcessFilterForm':
		"""
		Initiate object with values from request
		"""
		super(ProcessFilterForm, self).__init__('process')


class PlayerForm(FlaskForm):

	"""
	This is a PlayerForm class to retrieve form data.
	"""
	answer = StringField()
	submit = SubmitField()


def verify_process_owner(process: Process) -> bool:
	"""
	Return True when current_user is the process owner,
	otherwise return False.
	"""
	if process is None:
		return False
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
	filter = ProcessFilterForm()
	if filter.is_submit(filter.submit.label.text) and \
			filter.validate_on_submit(): # Valid post request
		filter.store_fields()
		return redirect(filter.url_for_with_fields('test.get_process'))
	filter.define_fields()
	# Prepare list data
	pagination = get_pagination(
		'process',
		ProcessStore.count_list(
			filter.name.data,
			filter.extension.data,
			filter.hide_completed.data,
			current_user.get_id(),
			current_user.get_token()
		)
	)
	pagination['endpoint'] = 'test.get_process'
	pagination['prefix'] = 'process'
	processes = ProcessStore.read_list(
		(pagination['page_index'] - 1) * pagination['per_page'],
		pagination['per_page'],
		filter.name.data,
		filter.extension.data,
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
	if current_user.is_authenticated and \
			current_user.user.notification_test_start:
		IdenticaPlugin.notify_user(
			current_user.user.from_id,
			process_template % (
				'%s (%s)' % (test.name, __(test.extension)),
				__('Started')
			)
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
	# Import extension module and get data
	extension_module = importlib.import_module('extensions.%s' % test.extension)
	data = extension_module.get_data(json.loads(test.extension_options))
	# Read previous tasks
	task = None
	passed_tasks = TaskStore.read_list(
		offset=0, limit=0, filter_process_id=process.id)
	if passed_tasks and passed_tasks[0].answer is None:
		# Continue on existing task
		task = passed_tasks[0]
		passed_tasks = passed_tasks[1:]
	# Handle filter form
	sound_filename = None
	player = PlayerForm()
	if player.validate_on_submit():
		user_answer, validation_errors = extension_module.validate_answer(request.form)
		if validation_errors: # Extension should validate anwser
			data = json.loads(task.data)
			player.answer.errors = validation_errors
		else:
			task = TaskStore.set_answer(task.uid, user_answer)
			process = ProcessStore.add_answer(process.uid, task)
			if process.result is not None:
				if current_user.is_authenticated and \
						current_user.user.notification_test_start:
					IdenticaExtension.notify_user(
						current_user.user.from_id,
						process_template % (
							'%s (%s)' % (test.name, __(test.extension)),
							__('Completed with result %s') % process.result + '%'
						)
					)
				return redirect(url_for('test.get_result', uid=uid))
			sound_filename = 'yay.mp3' if task.correct_answer else 'break.mp3'
			passed_tasks = [task] + passed_tasks
			task = TaskStore.create(process.id, json.dumps(data))
			player.answer.data = None
	elif task is None:
		task = TaskStore.create(process.id, json.dumps(data))
	else:
		data = json.loads(task.data)
	return render_template(
		'test/player.html',
		process=process,
		test=test,
		data=data,
		passed_tasks=passed_tasks,
		player=player,
		sound_filename=sound_filename,
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
	sound_filename = None
	utcnow = datetime.datetime.utcnow()
	if (utcnow - passed_tasks[0].modified_utc).total_seconds() < 5:
		sound_filename = 'yay.mp3' \
			if passed_tasks[0].correct_answer else 'break.mp3'
	return render_template(
		'test/result.html',
		process=process,
		test=test,
		passed_tasks=passed_tasks,
		sound_filename=sound_filename,
		nav_active='test'
	)
