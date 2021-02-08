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
from blueprints.__locale__ import __
from blueprints.__paginator__ import get_pagination
from blueprints.__args__ import get_string
from blueprints.__args__ import get_boolean
from blueprints.__args__ import set_value
from blueprints.__alert__ import AlertType
from blueprints.__alert__ import AlertButton
from blueprints.__alert__ import Alert
from config import PLUGIN_LIST
from models.test_store import TestStore

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
	name = StringField('filterName')
	plugin = StringField('filterPlugin')
	hide_global = BooleanField('filterHideGlobal')
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
			self.hide_global.data = get_boolean('filterHideGlobal')
		else:
			set_value('filterName', None)
			set_value('filterPlugin', None)
			set_value('filterHideGlobal', None)

	def store_fields(self) -> None:
		"""
		Set form fields to values from request.
		"""
		set_value('filterName', self.name.data)
		set_value('filterPlugin', self.plugin.data)
		set_value('filterHideGlobal', self.hide_global.data)

	def url_for_with_fields(self, endpoint: str) -> object:
		"""
		Return url_for with defined form fields
		"""
		return url_for(
			endpoint,
			filterName=self.name.data,
			filterPlugin=self.plugin.data,
			filterHideGlobal=self.hide_global.data
		)


class CreatorForm(FlaskForm):
	"""
	This is CreatorForm class to retrieve form data.
	"""
	plugin = SelectField('creatorPlugin', validators=[validators.DataRequired()])
	submit = SubmitField('creatorSubmit')

	def __init__(self) -> 'CreatorForm':
		"""
		Initiate object with plugin
		"""
		super(CreatorForm, self).__init__()
		self.plugin.choices = PLUGIN_LIST
		self.plugin.data = request.form.get(self.plugin.label.text)


class PluginOptionsField(StringField):
	"""
	This is PluginOptionsField class to handle form data.
	"""
	plugin_module = None

	def get_items(self) -> list:
		"""
		Form from plugin and return options items list.
		"""
		return self.plugin_module.form_options(self.data)

	def pre_validate(self, form):
		"""
		Prevalidate plugin options values and store string representation.
		"""
		self.data = self.plugin_module.parse_options(request.form)
		self.plugin_module.form_options(self.data, validate=True)


class TestForm(FlaskForm):
	"""
	This is TestForm class to retrieve form data.
	"""
	name = StringField('name', validators=[validators.DataRequired()])
	options = PluginOptionsField('options')
	repeat = SelectField('repeat', validators=[validators.DataRequired()])
	speed = SelectField('speed', validators=[validators.DataRequired()])
	submit = SubmitField('submit')

	def __init__(self, plugin_module: object, test: object = None) -> 'TestForm':
		"""
		Initiate object with plugin, repeat and preformance choices.
		"""
		super(TestForm, self).__init__()
		self.repeat.choices = [
			('5', '5'), ('10', '10'), ('15', '15'),('25', '25'),('50', '50')
		]
		self.speed.choices = [
			('25', __('Slow')), ('50', __('Normal')), ('100', __('Fast'))
		]
		self.options.plugin_module = plugin_module
		if test:
			self.name.data = test.name
			self.options.data = test.plugin_options
			self.repeat.data = str(test.repeat)
			self.speed.data = str(test.speed)
		else:
			for field in self:
				if field.name != 'csrf_token':
					field.data = request.form.get(field.label.text)


@blueprint.route('/', methods=('GET', 'POST'))
@blueprint.route('/catalog/', methods=('GET', 'POST'))
def get_catalog():
	"""
	Return test catalog page.
	"""
	# Handle filter form
	filter = FilterForm()
	if request.form.get('filterSubmit') and \
			filter.validate_on_submit(): # Valid post request
		filter.store_fields()
		return redirect(filter.url_for_with_fields('test.get_catalog'))
	filter.define_fields()
	# Handle creator form
	creator = CreatorForm()
	if request.form.get('creatorSubmit') and \
			creator.validate_on_submit(): # Valid post request
		return redirect(url_for(
			'test.create', plugin=creator.plugin.data))
	# Prepare list data
	pagination = get_pagination(
		 TestStore.count_list(
			filter.name.data,
			filter.plugin.data,
			filter.hide_global.data
		)
	)
	pagination['endpoint'] = 'test.get_catalog'
	tests =  TestStore.read_list(
		(pagination['page_index'] - 1) * pagination['per_page'],
		pagination['per_page'],
		filter.name.data,
		filter.plugin.data,
		filter.hide_global.data
	)
	return render_template(
		'test/catalog.html',
		filter=filter,
		creator=creator,
		tests=tests,
		pagination=pagination,
		nav_active='catalog'
	)


@blueprint.route('/catalog/create/<plugin>/', methods=('GET', 'POST'))
def create(plugin: str):
	"""
	Return create test page.
	"""
	try:
		plugin_module = importlib.import_module('plugins.%s' % plugin)
	except:
		logging.error('Plugin import error', exc_info=1)
		redirect(url_for('test.get_catalog'))
	creator = TestForm(plugin_module=plugin_module)
	if creator.validate_on_submit(): # Valid post request
		TestStore.create(
			creator.name.data,
			plugin,
			creator.options.data,
			int(creator.repeat.data),
			int(creator.speed.data)
		)
		return redirect(url_for('test.get_catalog'))
	return render_template(
		'test/editor.html',
		type='create',
		editor=creator,
		nav_active='catalog'
	)


@blueprint.route('/catalog/update/<uid>/', methods=('GET', 'POST'))
def update(uid: str):
	"""
	Return test update page.
	"""
	test = TestStore.read(uid)
	if test is None:
		return reidrect(url_for('test.get_catalog'))
	try:
		plugin_module = importlib.import_module('plugins.%s' % test.plugin)
	except:
		logging.error('Plugin import error', exc_info=1)
		redirect(url_for('test.get_catalog'))
	if request.method == 'GET':
		updater = TestForm(plugin_module, test)
	else:
		updater = TestForm(plugin_module)
	if updater.validate_on_submit(): # Valid post request
		TestStore.update(
			uid,
			updater.name.data,
			updater.options.data,
			int(updater.repeat.data),
			int(updater.speed.data)
		)
		return redirect(url_for('test.get_catalog'))
	return render_template(
		'test/editor.html',
		type='update',
		editor=updater,
		nav_active='catalog'
	)


@blueprint.route('/catalog/delete/<uid>/', methods=('GET',))
def delete(uid: str):
	"""
	Delete test and redirect to test catalog.
	"""
	TestStore.delete(uid)
	return redirect(url_for('test.get_catalog'))