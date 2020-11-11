# -*- coding: utf-8 -*-

"""
Blueprint module to handle examination catalog routes.
"""

# Standard libraries import
import datetime

# Application modules import
from blueprints import application
from blueprints.examination import blueprint
from blueprints.__paginator__ import get_pagination
from blueprints.__locale__ import __
from blueprints.__args__ import get_string
from blueprints.__args__ import get_boolean
from blueprints.__args__ import set_value

# Additional libraries import
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import BooleanField
from wtforms import SubmitField

# Test data
test_examinations = [
	{
		'uid': '1',
		'name': 'Test Examination 1',
		'description': 'Simple exmine for your kids',
		'plugin': 'arithmetics',
		'options': [],
		'created': datetime.datetime.utcnow(),
		'modified': datetime.datetime.utcnow(),
		'passed': datetime.datetime.utcnow(),
		'public': True,
		'score': 30
	},
	{
		'uid': '2',
		'name': 'Test Examination 2',
		'description': 'Simple exmine for your kids',
		'plugin': 'arithmetics',
		'options': [],
		'created': datetime.datetime.utcnow(),
		'modified': datetime.datetime.utcnow(),
		'passed': datetime.datetime.utcnow(),
		'public': True,
		'score': 30
	},
	{
		'uid': '3',
		'name': 'Test Examination 3',
		'description': 'Simple exmine for your kids',
		'plugin': 'arithmetics',
		'options': [],
		'created': datetime.datetime.utcnow(),
		'modified': datetime.datetime.utcnow(),
		'passed': datetime.datetime.utcnow(),
		'public': True,
		'score': 30
	}
]
test_examinations += test_examinations
test_examinations += test_examinations
test_examinations += test_examinations
test_examinations += test_examinations
test_examinations += test_examinations


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
		self.filter_name.data = get_string('filter_name')
		self.filter_plugin.data = get_string('filter_plugin')
		self.filter_hide_global.data = get_boolean('filter_hide_global')

	def store_fields(self) -> None:
		"""
		Set form fields to values from request.
		"""
		set_value('filter_name', self.filter_name.data)
		set_value('filter_plugin', self.filter_plugin.data)
		set_value('filter_hide_global', self.filter_hide_global.data)


class EditorForm(FlaskForm):
	"""
	This is EditorForm class to retrieve form data.
	"""
	editor_name = StringField()
	editor_description = StringField()
	submit = SubmitField()

	def __init__(self, item: dict) -> 'EditorForm':
		"""
		"""
		pass

	def set_fields_from_request(self) -> None:
		"""
		Set form fields to values from request.
		"""
		pass


@blueprint.route('/', methods=('GET', 'POST'))
@blueprint.route('/catalog/', methods=('GET', 'POST'))
def get_examination_catalog():
	"""
	Return examination catalog page.
	"""
	filter = FilterForm()
	if filter.validate_on_submit():
		filter.store_fields()
		return redirect(url_for(
			'examination.get_examination_catalog',
			filter_name=filter.filter_name.data,
			filter_plugin=filter.filter_plugin.data,
			filter_hide_global=filter.filter_hide_global.data
		))
	filter.define_fields()
	pagination = get_pagination(len(test_examinations))
	pagination['endpoint'] = 'examination.get_examination_catalog'
	examinations = test_examinations[
		(pagination['page_index'] - 1) * pagination['per_page']:
		pagination['page_index'] * pagination['per_page']
	]
	caption = __('%d examinations out of %d') % \
		(
			min(pagination['entity_count'], pagination['per_page']),
			pagination['entity_count']
		)
	return render_template(
		'examination/catalog.html',
		filter=filter,
		examinations=examinations,
		caption=caption,
		pagination=pagination
	)


@blueprint.route('/view/<uid>/', methods=('GET',))
def get_examination(uid: str):
	"""
	Return examination view page.
	"""
	item = test_examinations[0]
	return render_template(
		'examination/info.html',
		item=item
	)


@blueprint.route('/edit/<uid>/', methods=('GET', 'POST'))
def edit_examination(uid: str):
	"""
	Return examination edit page.
	"""
	item = test_examinations[0]
	editor = EditorForm(item)
	return render_template(
		'examination/edit.html',
		editor=editor,
		uid=uid
	)


@blueprint.route('/catalog/delete/<uid>/', methods=('GET',))
def delete_examination(uid: str):
	"""
	Return examination delete page.
	"""
	return 'Examination Delete Page'
