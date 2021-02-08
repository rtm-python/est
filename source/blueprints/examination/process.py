# -*- coding: utf-8 -*-

"""
Blueprint module to handle examination process routes.
"""

# Standard libraries import
import sys
import json
import datetime
import importlib
import logging

# Application modules import
from blueprints import application
from blueprints.examination import blueprint
from blueprints.__alert__ import AlertType
from blueprints.__alert__ import AlertButton
from blueprints.__alert__ import Alert
from models.examination_store import ExaminationStore
from models.process_store import ProcessStore
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
from wtforms import SubmitField
from wtforms import validators
from flask_login import current_user


class FilterForm(FlaskForm):
	"""
	This is FilterForm class to retrieve form data.
	"""
	filter_name = StringField()
	filter_plugin = StringField()
	filter_hide_global = BooleanField()
	submit = SubmitField()

	def define_fields(self) -> None:
		"""
		Set form fields to values from request.
		"""
		if not get_boolean('filter_reset'):
			self.filter_name.data = get_string('filter_name')
			self.filter_plugin.data = get_string('filter_plugin')
			self.filter_hide_global.data = get_boolean('filter_hide_global')
		else:
			set_value('filter_name', None)
			set_value('filter_plugin', None)
			set_value('filter_hide_global', None)

	def store_fields(self) -> None:
		"""
		Set form fields to values from request.
		"""
		set_value('filter_name', self.filter_name.data)
		set_value('filter_plugin', self.filter_plugin.data)
		set_value('filter_hide_global', self.filter_hide_global.data)


class StarterForm(FlaskForm):
	"""
	This is a StarterForm class to retrieve form data.
	"""
	repeat = SelectField(validators=[validators.DataRequired()])
	performance = SelectField(validators=[validators.DataRequired()])
	submit = SubmitField()

	def __init__(self, examination=None) -> 'StarterForm':
		"""
		Initiate object with repeat and preformance choices
		"""
		super(StarterForm, self).__init__()
		self.repeat.choices = [
			('5', '5'), ('10', '10'), ('15', '15'),('25', '25'),('50', '50')
		]
		self.performance.choices = [
			('25', '25%'), ('50', '50%'), ('75', '75%'), ('100', '100%')
		]
		if examination:
			self.repeat.data = str(examination.default_repeat)
			self.performance.data = str(examination.default_performance)


class PlayerForm(FlaskForm):
	"""
	This is a PlayerForm class to retrieve form data.
	"""
	answer = StringField(validators=[validators.DataRequired()])
	submit = SubmitField()


class ExaminationProgress:
	"""
	This is a ExaminationProgress class to provide examination statistics.
	"""

	def __init__(self, examination: Examination) -> 'ExaminationProgress':
		"""
		Initiate object with progress values.
		"""
		self.recents = ProcessStore.read_list(
			offset=0, limit=12, filter_examination_id=examination.id,
			user_uid=current_user.get_id(), anonymous_token=current_user.get_token()
		)
		answer_count = 0
		correct_count = 0
		for process in self.recents:
			answer_count += process.answer_count
			correct_count += process.correct_count
		if answer_count > 0:
			self.value = int(correct_count / answer_count * 100)
		else:
			self.value = 0
		self.modified_utc = self.recents[0].modified_utc \
			if self.recents else examination.modified_utc


def verify_process_owner(process: Process) -> bool:
	"""
	Return True when current_user is the process owner,
	otherwise return False.
	"""
	if current_user.get_id() is not None and \
			current_user.get_id() != process.user_uid:
		return False
	if current_user.get_token() is not None and \
			current_user.get_token() != process.anonymous_token:
		return False
	return True


@blueprint.route('/start/<uid>/', methods=('GET', 'POST'))
def start_examination(uid: str):
	"""
	Return start examination page.
	"""
	examination = ExaminationStore.read(uid)
	if request.method == 'GET':
		starter = StarterForm(examination)
	else:
		starter = StarterForm()
	if starter.validate_on_submit():
		process = ProcessStore.create(
			examination.id, examination.plugin, examination.plugin_options,
			examination.name, starter.repeat.data, starter.performance.data,
			current_user.get_id(), current_user.get_token()
		)
		return redirect(url_for(
			'examination.play_process', uid=process.uid))
	examination_progress = ExaminationProgress(examination)
	return render_template(
		'examination/process/starter.html',
		examination=examination,
		examination_progress=examination_progress,
		starter=starter
	)


@blueprint.route('/process/<uid>/play/', methods=('GET', 'POST'))
def play_process(uid: str):
	"""
	Return examination process page.
	"""
	process = ProcessStore.read(uid)
	if not verify_process_owner(process):
		examination = ExaminationStore.get(process.examination_id)
		return redirect(url_for(
			'examination.start_examination', uid=examination.uid))
	plugin_module = importlib.import_module('plugins.%s' % process.plugin)
	answer_alert = None # To show in/correctness of answer
	do_get = False
	while True:
		# Loop is used to refresh player form and flash modal message
		tasks = TaskStore.read_list(
			offset=0, limit=1, filter_process_id=process.id
		)
		if tasks and tasks[0].answer is None:	# Continue on existing task
			task = tasks[0]
			data = json.loads(task.data)
		else:  # (normal behavior) Continue with creating new task
			if process.answer_count >= process.repeat:
				# Process complete (all tasks answered)
				return redirect(
					url_for('examination.show_process_result', uid=process.uid)
				)
			data = plugin_module.get_data(json.loads(process.plugin_options))
			task = TaskStore.create(process.id, json.dumps(data))
		player = PlayerForm()
		if player.validate_on_submit() and not do_get:
			# Validate only once (on loop do_get prevents validation)
			user_answer = player.answer.data.strip()
			validation_errors = plugin_module.validate_answer(user_answer)
			if validation_errors: # Plugin should validate anwser
				player.answer.errors = validation_errors
				do_get = True
				break
			task = TaskStore.set_answer(task.uid, user_answer)
			ProcessStore.add_answer(process.uid, task)
			if data['answer'] == user_answer:
				message = '%s is correct answer!'
			else:
				message = 'Incorrect answer! Correct is %s...'
			answer_alert = Alert(process.name, message, (data['answer'],), [])
			do_get = True
		else:
			break
	if do_get:
		player.answer.data = ''
	return render_template(
		'examination/process/player.html',
		process=process,
		player=player,
		data=data,
		alert=answer_alert
	)


@blueprint.route('/process/<uid>/stop/', methods=('GET',))
def stop_process(uid: str):
	"""
	Remove current task and redirect to start examination page.
	"""
	process = ProcessStore.read(uid)
	if not verify_process_owner(process):
		examination = ExaminationStore.get(process.examination_id)
		return redirect(url_for(
			'examination.start_examination', uid=examination.uid))
	tasks = TaskStore.read_list(
		offset=0, limit=1, filter_process_id=process.id
	)
	if len(tasks) == 1:
		task = tasks[0]
		TaskStore.delete(task.uid)
	examination = ExaminationStore.get(process.examination_id)
	return redirect(
		url_for('examination.start_examination', uid=examination.uid)
	)


@blueprint.route('/process/<uid>/result/', methods=('GET',))
def show_process_result(uid: str):
	"""
	Return process result page.
	"""
	process = ProcessStore.read(uid)
	if not verify_process_owner(process):
		examination = ExaminationStore.get(process.examination_id)
		return redirect(url_for(
			'examination.start_examination', uid=examination.uid))
	return render_template(
		'examination/process/result.html',
		process=process
	)
