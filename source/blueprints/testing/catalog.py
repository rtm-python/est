# -*- coding: utf-8 -*-

"""
Blueprint module to handle test catalog routes.
"""

# Standard libraries import
import importlib
import logging

# Application modules import
from blueprints import application
from blueprints.testing import blueprint
from blueprints.__locale__ import __
from blueprints.__pagination__ import get_pagination
from blueprints.__args__ import get_boolean
from config import EXTENSION_LIST
from models.test_store import TestStore
from models.entity.test import Test

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


CATALOG_FILTERS = [
	{
		'name': 'filterCatalogHideGlobal',
		'label': {
			False: 'Hide Global Tasks',
			True: 'Show Global Tasks'
		}
	}
]


class ExtensionOptionsField(StringField):
	"""
	This is ExtensionOptionsField class to handle form data.
	"""
	extension_module = None

	def get_items(self) -> list:
		"""
		Form from extension and return options items list.
		"""
		return self.extension_module.form_options(self.data)

	def pre_validate(self, form):
		"""
		Prevalidate extension options values and store string representation.
		"""
		self.data = self.extension_module.parse_options(request.form)
		self.extension_module.form_options(self.data, validate=True)


class TestForm(FlaskForm):
	"""
	This is TestForm class to retrieve form data.
	"""
	name = StringField('name', validators=[validators.DataRequired()])
	options = ExtensionOptionsField('options')
	answer_count = SelectField('answer_count', validators=[validators.DataRequired()])
	submit = SubmitField('submit')

	def __init__(self, extension_module: object, test: object = None) -> 'TestForm':
		"""
		Initiate object with extension, repeat and preformance choices.
		"""
		super(TestForm, self).__init__()
		self.answer_count.choices = [
			('5', '5'), ('10', '10'), ('15', '15'),('25', '25'),('50', '50')
		]
		self.options.extension_module = extension_module
		if test:
			self.name.data = test.name
			self.options.data = test.extension_options
			self.answer_count.data = str(test.answer_count)
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
			current_user.get_id() != test.user_uid and \
				current_user.get_id() not in current_user.get_admin_uid_list():
		return False
	return True


@blueprint.route('/', methods=('GET', 'POST'))
def get_catalog():
	"""
	Return testing catalog page.
	"""
	# Filters
	filters = []
	if current_user.is_authenticated:
		start_index = 0
	else:
		start_index = 1
	for filter in CATALOG_FILTERS[start_index: ]:
		filter_value = get_boolean(filter['name']) or False
		filters += [
			{
				'name': filter['name'],
				'label': filter['label'][filter_value],
				'value': filter_value,
				'url': url_for(
					'testing.get_catalog',
					**{ filter['name']: not filter_value }
				)
			}
		]
	# Prepare list data
	filter_hide_global = filters[0]['value'] \
		if current_user.is_authenticated else None
	pagination = get_pagination(
		'catalog',
		 TestStore.count_list(
			None, None, current_user.get_id(),
			current_user.get_admin_uid_list() if not filter_hide_global else []
		)
	)
	pagination['endpoint'] = 'testing.get_catalog'
	pagination['prefix'] = 'catalog'
	tests =  TestStore.read_list(
		(pagination['page_index'] - 1) * pagination['per_page'],
		pagination['per_page'],
		None, None, current_user.get_id(),
		current_user.get_admin_uid_list() if not filter_hide_global else []
	)
	return render_template(
		'testing/catalog.html',
		filters=filters,
		tests=tests,
		pagination=pagination
	)


@blueprint.route('/create/', methods=('GET', 'POST'))
@blueprint.route('/create/<extension>/', methods=('GET', 'POST'))
def create(extension: str = None):
	"""
	Return create test page.
	"""
	if not current_user.is_authenticated:
		return redirect(url_for('testing.get_catalog'))
	if extension is not None:
		try:
			extension_module = importlib.import_module('extensions.%s' % extension)
		except:
			logging.error('Extension import error', exc_info=1)
			redirect(url_for('testing.get_catalog'))
		creator = TestForm(extension_module=extension_module)
		if creator.validate_on_submit():
			TestStore.create(
				creator.name.data,
				extension,
				creator.options.data,
				int(creator.answer_count.data),
				current_user.get_id()
			)
			return redirect(url_for('testing.get_catalog'))
	else:
		creator = None
	return render_template(
		'testing/editor.html',
		extensions=EXTENSION_LIST,
		current_extension=extension,
		editor=creator,
	)


@blueprint.route('/update/<uid>/', methods=('GET', 'POST'))
def update(uid: str):
	"""
	Return update test page.
	"""
	if not current_user.is_authenticated:
		return redirect(url_for('testing.get_catalog'))
	test = TestStore.read(uid)
	if not verify_test_owner(test):
		return reidrect(url_for('testing.get_catalog'))
	try:
		extension_module = importlib.import_module('extensions.%s' % test.extension)
	except:
		logging.error('Extension import error', exc_info=1)
		redirect(url_for('test.get_catalog'))
	if request.method == 'GET':
		updater = TestForm(extension_module, test)
	else:
		updater = TestForm(extension_module)
	if updater.validate_on_submit():
		TestStore.update(
			uid,
			updater.name.data,
			updater.options.data,
			int(updater.answer_count.data)
		)
		return redirect(url_for('testing.get_catalog'))
	return render_template(
		'testing/editor.html',
		current_extension=test.extension,
		editor=updater
	)


@blueprint.route('/delete/<uid>/', methods=('GET',))
def delete(uid: str):
	"""
	Delete test and redirect to testing catalog.
	"""
	if not current_user.is_authenticated:
		return redirect(url_for('testing.get_catalog'))
	test = TestStore.read(uid)
	if not verify_test_owner(test):
		return reidrect(url_for('testing.get_catalog'))
	TestStore.delete(uid)
	return redirect(url_for('testing.get_catalog'))
