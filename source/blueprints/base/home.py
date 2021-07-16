# -*- coding: utf-8 -*-

"""
Blueprint module to handle landing routes.
"""

# Application modules import
from blueprints import application
from blueprints.base import blueprint
from blueprints.__locale__ import __
from models.name_store import NameStore

# Additional libraries import
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from flask_login import current_user


class NamerForm(FlaskForm):
	"""
	This is a NamerForm class to retrieve form data.
	"""
	value = StringField('namerValue')
	submit = SubmitField('namerSubmit')

	def __init__(self) -> "NamerForm":
		"""
		Initiate object with values from request.
		"""
		super(NamerForm, self).__init__()
		for field in self:
			if field.name != 'csrf_token':
				data = request.form.get(field.label.text)
				field.data = data if data is not None and len(data) > 0 else None


@blueprint.route('/', methods=('GET', 'POST'))
def get_home():
	"""
	Return home page.
	"""
	names = []
	if current_user.is_authenticated:
		for name in NameStore.read_list(None, None, current_user.user.id, None):
			names += [(name.uid, name.value)]
	namer = NamerForm()
	if namer.validate_on_submit() and current_user.is_authenticated:
		if namer.value.data is None or len(namer.value.data.strip()) == 0:
			namer.value.errors = [ __('Empty value') ]
		else:
			name = NameStore.create(
				current_user.user.id, namer.value.data.strip())
			session['name'] = name.uid
			return redirect(url_for('testing.get_catalog'))
	return render_template(
		'base/home.html',
		names=names,
		namer=namer
	)


@blueprint.route('/name/<uid>/', methods=('GET',))
def select_name(uid: str):
	"""
	Select name and return redirect to testing.
	"""
	if not current_user.is_authenticated:
		return redirect(url_for('base.get_home'))
	name = NameStore.read(uid)
	if name is not None and name.user_id == current_user.user.id:
		session['name'] = name.uid
		return redirect(url_for('testing.get_catalog'))
	return redirect(url_for('base.get_home'))
