# -*- coding: utf-8 -*-

"""
Blueprint module to handle testing player routes.
"""

# Standard libraries import
import json
import datetime
import importlib
import logging

# Application modules import
from blueprints import application
from blueprints.testing import blueprint
from blueprints.__locale__ import __
from models.process_store import ProcessStore
from models.test_store import TestStore
from models.task_store import TaskStore
from models.name_store import NameStore
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
from wtforms import SubmitField
from flask_login import current_user
from sqlalchemy import func

# Global constants
process_template = __('TEST') + ': %s\n' + __('STATUS') + ': %s'


class PlayerForm(FlaskForm):

	"""
	This is a PlayerForm class to retrieve form data.
	"""
	answer = StringField()
	submit = SubmitField()


def verify_process_owner(process: Process,
												 ignore_name: bool = False) -> bool:
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
	if not ignore_name and current_user.get_name() is not None and \
			current_user.get_name().uid != process.name_uid:
		return False
	return True


@blueprint.route('/<uid>/start/', methods=('GET',))
def start(uid: str):
	"""
	Start testing and redirect to testing player page.
	"""
	test = TestStore.read(uid)
	if test is None:
		return redirect(url_for('testing.get_catalog'))
	name = current_user.get_name()
	process = ProcessStore.create(
		test.id, current_user.get_id(), current_user.get_token(),
		name.uid if name is not None else None
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
	return redirect(url_for('testing.play', uid=process.uid))


@blueprint.route('/<uid>/play/', methods=('GET', 'POST'))
def play(uid: str):
	"""
	Return testing player page.
	"""
	process, test, _, _ = ProcessStore.read_with_test(uid)
	if not verify_process_owner(process):
		if request.method == 'POST' and request.form.get('ajax'):
			return { 'redirect': url_for('testing.get_catalog') }
		return redirect(url_for('testing.get_catalog'))
	if process.answer_count == test.answer_count:
		if request.method == 'POST' and request.form.get('ajax'):
			return { 'redirect': url_for('testing.get_result', uid=uid) }
		return redirect(url_for('testing.get_result', uid=uid))
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
	player_audio = None
	player = PlayerForm()
	if player.validate_on_submit():
		user_answer, validation_errors = extension_module.validate_answer(request.form)
		if validation_errors: # Extension should validate anwser
			data = json.loads(task.data)
			player.errors = validation_errors
		else:
			task = TaskStore.set_answer(task.uid, user_answer)
			process = ProcessStore.add_answer(process.uid, task)
			if process.answer_count == test.answer_count:
				if current_user.is_authenticated and \
							current_user.user.notification_test_complete:
					IdenticaPlugin.notify_user(
						current_user.user.from_id,
						process_template % (
							'%s (%s)' % (test.name, __(test.extension)),
							__('Completed with result %s') % process.result + '%'
						)
					)
				if request.form.get('ajax'):
					return { 'redirect': url_for('testing.get_result', uid=uid) }
				return redirect(url_for('test.get_result', uid=uid))
			player_audio = 'correct-audio' \
				if task.correct_answer else 'incorrect-audio'
			passed_tasks = [task] + passed_tasks
			task = TaskStore.create(process.id, json.dumps(data))
			player.answer.data = None
	elif task is None:
		task = TaskStore.create(process.id, json.dumps(data))
	else:
		data = json.loads(task.data)
	if request.method == 'POST' and request.form.get('ajax'):
		return {
			'form': render_template(
				'testing/form.html',
				test=test,
				data=data,
				player=player
			),
			'passed': render_template(
				'testing/passed.html',
				test=test,
				passed_task=passed_tasks[0]
			),
			'audio': player_audio
		}
	return render_template(
		'testing/player.html',
		process=process,
		test=test,
		data=data,
		passed_tasks=passed_tasks,
		player=player,
		player_audio=player_audio,
		nav_active='testing'
	)


@blueprint.route('/<uid>/break/', methods=('GET',))
def hold(uid: str):
	"""
	Hold testing and redirect to testing catalog page.
	"""
	process, test, _, _ = ProcessStore.read_with_test(uid)
	if not verify_process_owner(process):
		return redirect(url_for('testing.get_catalog'))
	if process.answer_count == test.answer_count:
		return redirect(url_for('testing.get_result', uid=uid))
	passed_tasks = TaskStore.read_list(
		offset=0, limit=0, filter_process_id=process.id)
	if passed_tasks and passed_tasks[0].answer is None:
		TaskStore.delete(passed_tasks[0].uid)
	process.answer_time += 10
	ProcessStore.update(
		process.uid, process.test_id, process.user_uid,
		process.anonymous_token, process.name_uid,
		process.answer_count, process.correct_count,
		process.limit_time, process.answer_time + 10
	)
	return redirect(url_for('testing.get_catalog'))


@blueprint.route('/<uid>/result/', methods=('GET',))
def get_result(uid: str):
	"""
	Return testing result page.
	"""
	process, test, result, crammers = ProcessStore.read_with_test(
		uid, get_result_expression(), get_crammers_expression())
	if not verify_process_owner(process, ignore_name=True):
		return redirect(url_for('testing.get_process', uid=uid))
	if process.answer_count < test.answer_count:
		return redirect(url_for('testing.play'))
	name = NameStore.read(process.name_uid)
	name_value = name.value if name is not None else ''
	# Read previous tasks
	passed_tasks = TaskStore.read_list(
		offset=0, limit=0, filter_process_id=process.id)
	player_audio = None
	utcnow = datetime.datetime.utcnow()
	if (utcnow - passed_tasks[0].modified_utc).total_seconds() < 3:
		player_audio = 'correct-audio' \
			if passed_tasks[0].correct_answer else 'incorrect-audio'
	return render_template(
		'testing/result.html',
		process=process,
		test=test,
		result=result,
		crammers=crammers,
		passed_tasks=passed_tasks,
		name_value=name_value,
		player_audio=player_audio,
		nav_active='testing'
	)


def get_result_expression():
	"""
	Return result calculation expression.
	"""
	return 1.0 * Process.correct_count / Process.answer_count * 100 * \
		func.min(1.0 * Process.limit_time / Process.answer_time, 1.0)


def get_crammers_expression():
	"""
	Return result calculation expression.
	"""
	return 1.0 * Process.correct_count / Process.answer_count * 100 * \
		func.min(1.0 * Process.limit_time / Process.answer_time, 1.0) * \
			Process.answer_count / Process.answer_time