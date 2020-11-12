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
from blueprints.__paginator__ import get_pagination
from blueprints.__locale__ import __
from blueprints.__args__ import get_string
from blueprints.__args__ import get_boolean
from blueprints.__args__ import set_value
from blueprints.__alert__ import AlertType
from blueprints.__alert__ import AlertButton
from blueprints.__alert__ import Alert
from models import examination_store
from models import process_store
from models import task_store

# Additional libraries import
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import BooleanField
from wtforms import SelectField
from wtforms import SubmitField
from wtforms import validators


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


class FollowerForm(FlaskForm):
	"""
	This is a FollowerForm class to retrieve form data.
	"""
	answer = StringField(validators=[validators.DataRequired()])
	submit = SubmitField()


@blueprint.route('/start/<uid>/', methods=('GET', 'POST'))
def start_examination(uid: str):
	"""
	Return start examination page.
	"""
	examination = examination_store.read_examination(uid)
	if request.method == 'GET':
		starter = StarterForm(examination)
	else:
		starter = StarterForm()
	if starter.validate_on_submit():
		process = process_store.create_process(
			examination.id, examination.plugin, examination.plugin_options,
			examination.name, starter.repeat.data, starter.performance.data
		)
		return redirect(url_for(
			'examination.follow_process', uid=process.uid))
	recent = process_store.read_process_list(0, 12, examination.id)
	return render_template(
		'examination/process/starter.html',
		examination=examination,
		starter=starter,
		recent=recent
	)


@blueprint.route('/process/<uid>/', methods=('GET', 'POST'))
def follow_process(uid: str):
	"""
	Return examination process page.
	"""
	process = process_store.read_process(uid)
	answer_alert = None
	do_get = False
	while True:
		tasks = task_store.read_task_list(0, 1, process.id)
		if len(tasks) == 1:
			task = tasks[0]
			data = json.loads(task.data)
		else:
			plugin_module = importlib.import_module('plugins.%s' % process.plugin)
			data = plugin_module.get_data(json.loads(process.plugin_options))
			task = task_store.create_task(process.id, json.dumps(data))
		follower = FollowerForm()
		if follower.validate_on_submit() and not do_get:
			user_answer = follower.answer.data.strip()
			task_store.set_answer(task.uid, user_answer)
			process_store.update_answered(
				process.uid, data['answer'] == user_answer)
			if data['answer'] == user_answer:
				message = '%s is correct answer!'
			else:
				message = 'Incorrect answer! Correct is %s...'
			answer_alert = Alert(process.name, message, (data['answer'],), [])
			do_get = True
		else:
			break
	if do_get:
		follower.answer.data = ''
	return render_template(
		'examination/process/follower.html',
		process=process,
		follower=follower,
		data=data,
		alert=answer_alert
	)


#
#@blueprint.route('/create/', methods=('GET', 'POST'))
#def create_examination():
#	"""
#	Return examination create page.
#	"""
#	creator = ExaminationForm()
#	is_plugin = False
#	options = None
#	if 'save' in request.form:
#		# Saving examination
#		if creator.validate_on_submit():
#			if creator.plugin.data in PLUGIN_LIST:
#				try:
#					plugin_module = importlib.import_module(
#						'plugins.%s' % creator.plugin.data)
#					options = plugin_module.form_options(
#						creator.plugin_options.data, True)
#					examination_store.create_examination(
#						creator.name.data,
#						creator.description.data,
#						creator.plugin.data,
#						creator.plugin_options.data,
#						int(creator.default_repeat.data),
#						int(creator.default_performance.data)
#					)
#					return redirect(url_for('examination.get_examination_catalog'))
#				except Exception as exc:
#					logging.error(getattr(exc, 'message', repr(exc)))
#					creator.plugin_options.errors = ('Options error.',)
#	elif 'apply_plugin' in request.form:
#		# Applying plugin options
#		if creator.validate_on_submit():
#			if creator.plugin.data in PLUGIN_LIST:
#				try:
#					plugin_module = importlib.import_module(
#						'plugins.%s' % creator.plugin.data)
#					creator.plugin_options.data = \
#						plugin_module.parse_options(request.form)
#				except Exception as exc:
#					logging.error(getattr(exc, 'message', repr(exc)))
#					creator.plugin_options.errors = ('Options error.',)
#	elif 'configure_plugin' in request.form:
#		# Configure plugin options
#		if creator.validate_on_submit():
#			if creator.plugin.data in PLUGIN_LIST:
#				try:
#					plugin_module = importlib.import_module(
#						'plugins.%s' % creator.plugin.data)
#					options = plugin_module.form_options(
#						creator.plugin_options.data)
#					is_plugin = True
#				except Exception as exc:
#					logging.error(getattr(exc, 'message', repr(exc)))
#					creator.plugin.errors = ('Plugin error.',)
#	return render_template(
#		'examination/catalog/creator.html',
#		creator=creator,
#		is_plugin=is_plugin,
#		options=options
#	)
#
#
#@blueprint.route('/update/<uid>/', methods=('GET', 'POST'))
#def update_examination(uid: str):
#	"""
#	Return examination update page.
#	"""
#	if request.method == 'GET':
#		updater = ExaminationForm(examination_store.read_examination(uid))
#	else:
#		updater = ExaminationForm()
#	is_plugin = False
#	options = None
#	if 'save' in request.form:
#		# Saving examination
#		if updater.validate_on_submit():
#			if updater.plugin.data in PLUGIN_LIST:
#				try:
#					plugin_module = importlib.import_module(
#						'plugins.%s' % updater.plugin.data)
#					options = plugin_module.form_options(
#						updater.plugin_options.data, True)
#					examination_store.update_examination(
#						uid,
#						updater.name.data,
#						updater.description.data,
#						updater.plugin.data,
#						updater.plugin_options.data,
#						int(updater.default_repeat.data),
#						int(updater.default_performance.data)
#					)
#					return redirect(url_for('examination.get_examination_catalog'))
#				except Exception as exc:
#					logging.error(getattr(exc, 'message', repr(exc)))
#					updater.plugin_options.errors = ('Options error.',)
#	elif 'apply_plugin' in request.form:
#		# Applying plugin options
#		if updater.validate_on_submit():
#			if updater.plugin.data in PLUGIN_LIST:
#				try:
#					plugin_module = importlib.import_module(
#						'plugins.%s' % updater.plugin.data)
#					updater.plugin_options.data = \
#						plugin_module.parse_options(request.form)
#				except Exception as exc:
#					logging.error(getattr(exc, 'message', repr(exc)))
#					updater.plugin_options.errors = ('Options error.',)
#	elif 'configure_plugin' in request.form:
#		# Configure plugin options
#		if updater.validate_on_submit():
#			if updater.plugin.data in PLUGIN_LIST:
#				try:
#					plugin_module = importlib.import_module(
#						'plugins.%s' % updater.plugin.data)
#					options = plugin_module.form_options(
#						updater.plugin_options.data)
#					is_plugin = True
#				except Exception as exc:
#					logging.error(getattr(exc, 'message', repr(exc)))
#					updater.plugin.errors = ('Plugin error.',)
#	return render_template(
#		'examination/catalog/updater.html',
#		updater=updater,
#		is_plugin=is_plugin,
#		options=options
#	)
#
#
#@blueprint.route('/delete/<uid>/', methods=('GET',))
#def delete_examination(uid: str):
#	"""
#	Delete examination and redirect to examination catalog.
#	"""
#	examination_store.delete_examination(uid)
#	return redirect(url_for('examination.get_examination_catalog'))
