# -*- coding: utf-8 -*-

"""
Blueprint module to handle test catalog routes.
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
from config import PLUGIN_LIST
from models.examination_store import ExaminationStore
from blueprints.examination.process import ExaminationProgress

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
		if not get_boolean('filterReset'):
			self.filter_name.data = get_string('filterName')
			self.filter_plugin.data = get_string('filterPlugin')
			self.filter_hide_global.data = get_boolean('filterHideGlobal')
		else:
			set_value('filterName', None)
			set_value('filterPlugin', None)
			set_value('filterHideGlobal', None)

	def store_fields(self) -> None:
		"""
		Set form fields to values from request.
		"""
		set_value('filterName', self.filter_name.data)
		set_value('filterPlugin', self.filter_plugin.data)
		set_value('filterHideGlobal', self.filter_hide_global.data)

	def url_for_with_fields(self, endpoint: str) -> object:
		"""
		Return url_for with defined form fields
		"""
		return url_for(
			endpoint,
			filterName=filter.filter_name.data,
			filterPlugin=filter.filter_plugin.data,
			filterHideGlobal=filter.filter_hide_global.data
		)


class ExaminationForm(FlaskForm):
	"""
	This is ExaminationForm class to retrieve form data.
	"""
	name = StringField(validators=[validators.DataRequired()])
	description = StringField(validators=[validators.DataRequired()])
	plugin = SelectField(validators=[validators.DataRequired()])
	default_repeat = SelectField(validators=[validators.DataRequired()])
	default_performance = SelectField(validators=[validators.DataRequired()])
	plugin_options = StringField()
	submit = SubmitField()

	def __init__(self, examination=None) -> 'ExaminationForm':
		"""
		Initiate object with plugin, default_repeat and
		default_preformance choices
		"""
		super(ExaminationForm, self).__init__()
		self.plugin.choices = [
			('arithmetic', 'Arithmetic'),
			('word2word', 'Word Translation'),
			('image2word', 'Image Translation')
		]
		self.default_repeat.choices = [
			('5', '5'), ('10', '10'), ('15', '15'),('25', '25'),('50', '50')
		]
		self.default_performance.choices = [
			('25', '25%'), ('50', '50%'), ('75', '75%'), ('100', '100%')
		]
		if examination:
			self.name.data = examination.name
			self.description.data = examination.description
			self.plugin.data = examination.plugin
			self.plugin_options.data = examination.plugin_options
			self.default_repeat.data = str(examination.default_repeat)
			self.default_performance.data = str(examination.default_performance)


@blueprint.route('/', methods=('GET', 'POST'))
@blueprint.route('/catalog/', methods=('GET', 'POST'))
def get_catalog():
	"""
	Return test catalog page.
	"""

	delete_uid = request.args.get('delete_uid')
	if delete_uid:
		delete_alert = Alert(
			'Examination Catalog', 'Delete examination "%s"?',
			(ExaminationStore.read(delete_uid).name,),
			[
				AlertButton(
					AlertType.DARK,
					url_for('examination.delete_examination', uid=delete_uid),
					'Delete'
				)
			]
		)
	else:
		delete_alert = None
	# Handle filter form
	filter = FilterForm()
	if filter.validate_on_submit(): # Valid post request
		filter.store_fields()
		return redirect(filter.url_for_with_fields('test.get_catalog'))
	filter.define_fields()
	# Prepare list data
	pagination = get_pagination(
		 ExaminationStore.count_list(
			filter.filter_name.data,
			filter.filter_plugin.data,
			filter.filter_hide_global.data
		)
	)
	pagination['endpoint'] = 'test.get_catalog'
	examinations =  ExaminationStore.read_list(
		(pagination['page_index'] - 1) * pagination['per_page'],
		pagination['per_page'],
		filter.filter_name.data,
		filter.filter_plugin.data,
		filter.filter_hide_global.data
	)
	examinations_with_progress = []
	for examination in examinations:
		examinations_with_progress += [
			(examination, ExaminationProgress(examination))
		]
	return render_template(
		'test/catalog/catalog.html',
		filter=filter,
		testing=examinations_with_progress,
		pagination=pagination,
		nav_active='catalog'
	)


@blueprint.route('/create/', methods=('GET', 'POST'))
def create_examination():
	"""
	Return examination create page.
	"""
	creator = ExaminationForm()
	is_plugin = False
	options = None
	if 'save' in request.form:
		# Saving examination
		if creator.validate_on_submit():
			if creator.plugin.data in PLUGIN_LIST:
				try:
					plugin_module = importlib.import_module(
						'plugins.%s' % creator.plugin.data)
					options = plugin_module.form_options(
						creator.plugin_options.data, True)
					ExaminationStore.create(
						creator.name.data,
						creator.description.data,
						creator.plugin.data,
						creator.plugin_options.data,
						int(creator.default_repeat.data),
						int(creator.default_performance.data)
					)
					return redirect(url_for('examination.get_examination_catalog'))
				except Exception as exc:
					logging.error(getattr(exc, 'message', repr(exc)))
					creator.plugin_options.errors = ('Options error.',)
	elif 'apply_plugin' in request.form:
		# Applying plugin options
		if creator.validate_on_submit():
			if creator.plugin.data in PLUGIN_LIST:
				try:
					plugin_module = importlib.import_module(
						'plugins.%s' % creator.plugin.data)
					creator.plugin_options.data = \
						plugin_module.parse_options(request.form)
				except Exception as exc:
					logging.error(getattr(exc, 'message', repr(exc)))
					creator.plugin_options.errors = ('Options error.',)
	elif 'configure_plugin' in request.form:
		# Configure plugin options
		if creator.validate_on_submit():
			if creator.plugin.data in PLUGIN_LIST:
				try:
					plugin_module = importlib.import_module(
						'plugins.%s' % creator.plugin.data)
					options = plugin_module.form_options(
						creator.plugin_options.data)
					is_plugin = True
				except Exception as exc:
					logging.error(getattr(exc, 'message', repr(exc)))
					creator.plugin.errors = ('Plugin error.',)
	return render_template(
		'examination/catalog/creator.html',
		creator=creator,
		is_plugin=is_plugin,
		options=options
	)


@blueprint.route('/update/<uid>/', methods=('GET', 'POST'))
def update_examination(uid: str):
	"""
	Return examination update page.
	"""
	if request.method == 'GET':
		updater = ExaminationForm(ExaminationStore.read(uid))
	else:
		updater = ExaminationForm()
	is_plugin = False
	options = None
	if 'save' in request.form:
		# Saving examination
		if updater.validate_on_submit():
			if updater.plugin.data in PLUGIN_LIST:
				try:
					plugin_module = importlib.import_module(
						'plugins.%s' % updater.plugin.data)
					options = plugin_module.form_options(
						updater.plugin_options.data, True)
					print(updater.plugin_options.data)
					ExaminationStore.update(
						uid,
						updater.name.data,
						updater.description.data,
						updater.plugin.data,
						updater.plugin_options.data,
						int(updater.default_repeat.data),
						int(updater.default_performance.data)
					)
					return redirect(url_for('examination.get_examination_catalog'))
				except Exception as exc:
					logging.error(getattr(exc, 'message', repr(exc)))
					updater.plugin_options.errors = ('Options error.',)
	elif 'apply_plugin' in request.form:
		# Applying plugin options
		if updater.validate_on_submit():
			if updater.plugin.data in PLUGIN_LIST:
				try:
					plugin_module = importlib.import_module(
						'plugins.%s' % updater.plugin.data)
					updater.plugin_options.data = \
						plugin_module.parse_options(request.form)
				except Exception as exc:
					logging.error(getattr(exc, 'message', repr(exc)))
					updater.plugin_options.errors = ('Options error.',)
	elif 'configure_plugin' in request.form:
		# Configure plugin options
		if updater.validate_on_submit():
			if updater.plugin.data in PLUGIN_LIST:
				try:
					plugin_module = importlib.import_module(
						'plugins.%s' % updater.plugin.data)
					options = plugin_module.form_options(
						updater.plugin_options.data)
					is_plugin = True
				except Exception as exc:
					logging.error(getattr(exc, 'message', repr(exc)))
					updater.plugin.errors = ('Plugin error.',)
	return render_template(
		'examination/catalog/updater.html',
		updater=updater,
		is_plugin=is_plugin,
		options=options
	)


@blueprint.route('/delete/<uid>/', methods=('GET',))
def delete_examination(uid: str):
	"""
	Delete examination and redirect to examination catalog.
	"""
	ExaminationStore.delete(uid)
	return redirect(url_for('examination.get_examination_catalog'))
