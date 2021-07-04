# -*- coding: utf-8 -*-

"""
Blueprint module to handle name routes.
"""

# Standard libraries import
import logging

# Application modules import
from blueprints import application
from blueprints.base import blueprint
from blueprints.__locale__ import __
from models.name_store import NameStore
from models.entity.name import Name
from config import CONFIG

# Additional libraries import
from flask_login import current_user
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import RadioField
from wtforms import SubmitField
from wtforms import validators


class SwitcherForm(FlaskForm):
	"""
	This is a SwitcherForm class to retrieve form data.
	"""
	name = RadioField('switcherName')
	value = StringField('switcherValue')
	submit = SubmitField('switcherSubmit')

	def __init__(self) -> "SwitcherForm":
		"""
		Initiate object with values from request.
		"""
		super(SwitcherForm, self).__init__()
		self.name.choices = []
		for name in NameStore.read_list(None, None, current_user.user.id, None):
			self.name.choices += [(name.uid, name.value)]
		self.name.choices += [('new_name', __('New Name'))]
		for field in self:
			if field.name != 'csrf_token':
				data = request.form.get(field.label.text)
				field.data = data if data is not None and len(data) > 0 else None


@blueprint.route('/name/', methods=('GET', 'POST'))
@blueprint.route('/name/switcher/', methods=('GET', 'POST'))
def get_switcher():
	"""
	Return switcher page.
	"""
	if current_user.is_authenticated:
		switcher = SwitcherForm()
		if request.form.get('switcherSubmit') and \
				switcher.validate_on_submit(): # Valid post request
			if switcher.name.data == switcher.name.choices[-1][0]:
				if len(switcher.value.data.strip()) > 0:
					name = NameStore.create(
						current_user.user.id, switcher.value.data.strip())
			else:
				name = NameStore.read(switcher.name.data)
				if name is not None and name.user_id != current_user.user.id:
					name = None
			if name is not None:
				session['name'] = name.uid
				return redirect(url_for('base.get_landing'))
	else:
		switcher = None
	return render_template(
		'base/switcher.html',
		switcher=switcher,
		nav_active='name'
	)


@application.context_processor
def get_name():
	"""
	Return name from session.
	"""
	def _name(key: str) -> object:
		return __name()
	return dict(__name=__name)


def __name() -> object:
	"""
	Return name from session.
	"""
	name = session.get('name')
	if name:
		name = NameStore.read(name)
		if name:
			return name.value
	return None
