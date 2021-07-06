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


class UpdaterForm(FlaskForm):
	"""
	This is a UpdaterForm class to retrieve form data.
	"""
	uid = StringField('updaterUid')
	value = StringField('updaterValue')
	submit = SubmitField('updaterSubmit')

	def __init__(self) -> "UpdaterForm":
		"""
		Initiate object with values from request.
		"""
		super(UpdaterForm, self).__init__()
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
				if switcher.value.data and len(switcher.value.data.strip()) > 0:
					name = NameStore.create(
						current_user.user.id, switcher.value.data.strip())
					session['name'] = name.uid
					return redirect(url_for('base.get_landing'))
			else:
				name = NameStore.read(switcher.name.data)
				if name is not None and name.user_id == current_user.user.id:
					session['name'] = name.uid
					return redirect(url_for('base.get_landing'))
		updater = UpdaterForm()
		if request.form.get('updaterSubmit') and \
				updater.validate_on_submit(): # Valid post request
			if updater.value.data and len(updater.value.data.strip()) > 0:
				name = NameStore.read(updater.uid.data)
				if name is not None and name.user_id == current_user.user.id:
					name = NameStore.set_value(name.uid, updater.value.data.strip())
					for index in range(len(switcher.name.choices)):
						if switcher.name.choices[index][0] == name.uid:
							switcher.name.choices[index] = (name.uid, name.value)
							break
	else:
		switcher = None
		updater = None
	return render_template(
		'base/switcher.html',
		switcher=switcher,
		updater=updater,
		nav_active='name'
	)

@blueprint.route('/name/delete/<uid>/', methods=('GET',))
def delete_name(uid: str):
	"""
	Delete name and redirect to switcher.
	"""
	if current_user.is_authenticated:
		name = NameStore.read(uid)
		if name is not None and name.user_id == current_user.user.id:
			NameStore.delete(uid)
	return redirect(url_for('base.get_switcher'))
