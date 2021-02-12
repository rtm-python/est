# -*- coding: utf-8 -*-

"""
Blueprint module to handle scoreboard chart routes.
"""

# Standard libraries import
import sys
import json
import datetime
import importlib
import logging

# Application modules import
from blueprints.__args__ import get_string
from blueprints.__args__ import get_boolean
from blueprints.__args__ import set_value
from blueprints.__locale__ import __

# Additional libraries import
from flask import request
from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SelectField
from wtforms import BooleanField


class FilterForm(FlaskForm):
	"""
	This is FilterForm class to retrieve form data.
	"""
	__abstract__ = True
	prefix = None

	def __init__(self, prefix: str) -> 'FilterForm':
		"""
		Initiate object with values from request
		"""
		super(FilterForm, self).__init__()
		self.prefix = prefix
		for field in self:
			if field.name != 'csrf_token':
				data = request.form.get(self.prefix + field.label.text)
				field.data = data if data is not None and len(data) > 0 else None

	def define_fields(self) -> None:
		"""
		Set form fields to values from request.
		"""
		if get_boolean(self.prefix + 'FilterReset'):
			for field in self:
				if type(field) is StringField or \
						type(field) is SelectField or type(field) is BooleanField:
					set_value(self.prefix + field.label.text, None)
		else:
			for field in self:
				print(type(field), type(StringField),  type(field) is StringField)
				if type(field) is StringField:
					field.data = get_string(self.prefix + field.label.text)
				elif type(field) is SelectField:
					field.data = get_string(self.prefix + field.label.text)
				elif type(field) is BooleanField:
					field.data = get_boolean(self.prefix + field.label.text)

	def store_fields(self) -> None:
		"""
		Set form fields to values from request.
		"""
		for field in self:
			if type(field) is StringField or \
					type(field) is SelectField or type(field) is BooleanField:
				set_value(self.prefix + field.label.text, field.data)

	def url_for_with_fields(self, endpoint: str) -> object:
		"""
		Return url_for with defined form fields.
		"""
		filter_kwargs = {}
		for field in self:
			if type(field) is StringField or \
					type(field) is SelectField or type(field) is BooleanField:
				filter_kwargs[self.prefix + field.label.text] = field.data
		return url_for(endpoint, **filter_kwargs)

	def is_submit(self, submit_name: str) -> bool:
		"""
		Return True if submit is presented otherwise False.
		"""
		return request.form.get(self.prefix + submit_name)
