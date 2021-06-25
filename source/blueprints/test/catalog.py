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
from blueprints.__filter__ import FilterForm
from blueprints.__locale__ import __
from blueprints.__pagination__ import get_pagination
from blueprints.__args__ import get_string
from blueprints.__args__ import get_boolean
from blueprints.__args__ import set_value
from config import PLUGIN_LIST
from models.test_store import TestStore
from models.entity.test import Test

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
from flask_login import current_user


class CatalogFilterForm(FilterForm):
	"""
	This is CatalogFilterForm class to retrieve form data.
	"""
	name = StringField('FilterName')
	plugin = StringField('FilterPlugin')
	hide_global = BooleanField('FilterHideGlobal')
	submit = SubmitField('FilterSubmit')

	def __init__(self) -> 'CatalogFilterForm':
		"""
		Initiate object with values from request
		"""
		super(CatalogFilterForm, self).__init__('catalog')


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
			('25', 'Slow'), ('50', 'Normal'), ('100', 'Fast')
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


def verify_test_owner(test: Test) -> bool:
	"""
	Return True when current_user is the test owner,
	otherwise return False
	"""
	if test is None:
		return False
	if current_user.get_id() is not None and \
			current_user.get_id() != test.user_uid:
		return False
	return True


@blueprint.route('/', methods=('GET', 'POST'))
@blueprint.route('/catalog/', methods=('GET', 'POST'))
def get_catalog():
	"""
	Return test catalog page.
	"""
	# Handle filter form
	filter = CatalogFilterForm()
	if filter.is_submit(filter.submit.label.text) and \
			filter.validate_on_submit(): # Valid post request
		filter.store_fields()
		return redirect(filter.url_for_with_fields('test.get_catalog'))
	filter.define_fields()
	# Handle creator form
	creator = CreatorForm()
	if current_user.is_authenticated:
		if request.form.get('creatorSubmit') and \
				creator.validate_on_submit(): # Valid post request
			return redirect(url_for(
				'test.create', plugin=creator.plugin.data))
	# Prepare list data
	pagination = get_pagination(
		'catalog',
		 TestStore.count_list(
			filter.name.data,
			filter.plugin.data,
			current_user.get_id() if filter.hide_global.data else None
		)
	)
	pagination['endpoint'] = 'test.get_catalog'
	pagination['prefix'] = 'catalog'
	tests =  TestStore.read_list(
		(pagination['page_index'] - 1) * pagination['per_page'],
		pagination['per_page'],
		filter.name.data,
		filter.plugin.data,
		current_user.get_id() if filter.hide_global.data else None
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
	if not current_user.is_authenticated:
		return redirect(url_for('test.get_catalog'))
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
			int(creator.speed.data),
			current_user.get_id()
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
	if not current_user.is_authenticated:
		return redirect(url_for('test.get_catalog'))
	test = TestStore.read(uid)
	if not verify_test_owner(test):
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
	test = TestStore.read(uid)
	if not verify_test_owner(test):
		return reidrect(url_for('test.get_catalog'))
	TestStore.delete(uid)
	return redirect(url_for('test.get_catalog'))
