# -*- coding: utf-8 -*-

"""
Blueprint module to handle examination catalog routes.
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
from config import PLUGIN_LIST
from models import examination_store

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
		if not get_boolean('filter_reset'):
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


class CreatorForm(FlaskForm):
	"""
	This is CreatorForm class to retrieve form data.
	"""
	name = StringField(validators=[validators.DataRequired()])
	description = StringField(validators=[validators.DataRequired()])
	plugin = SelectField(validators=[validators.DataRequired()])
	default_repeat = SelectField(validators=[validators.DataRequired()])
	default_performance = SelectField(validators=[validators.DataRequired()])
	plugin_options = StringField()
	submit = SubmitField()

	def __init__(self) -> 'CreatorForm':
		"""
		Initiate object with plugin, default_repeat and
		default_preformance choices
		"""
		super(CreatorForm, self).__init__()
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
	pagination = get_pagination(
		 examination_store.count_examination_list(
			filter.filter_name.data,
			filter.filter_plugin.data,
			filter.filter_hide_global.data
		)
	)
	pagination['endpoint'] = 'examination.get_examination_catalog'
	examinations =  examination_store.read_examination_list(
		(pagination['page_index'] - 1) * pagination['per_page'],
		pagination['per_page'],
		filter.filter_name.data,
		filter.filter_plugin.data,
		filter.filter_hide_global.data
	)
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
	return render_template(
		'examination/info.html',
		item=examination_store.read_examination(uid)
	)


@blueprint.route('/create/', methods=('GET', 'POST'))
def create_examination():
	"""
	Return examination create page.
	"""
	creator = CreatorForm()
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
					examination_store.create_examination(
						creator.name.data,
						creator.description.data,
						creator.plugin.data,
						creator.plugin_options.data,
						creator.default_repeat.data,
						creator.default_performance.data
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
		'examination/creator.html',
		creator=creator,
		is_plugin=is_plugin,
		options=options
	)


@blueprint.route('/edit/<uid>/', methods=('GET', 'POST'))
def edit_examination(uid: str):
	"""
	Return examination edit page.
	"""
	editor = EditorForm(examination_store.read_examination(uid))
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
