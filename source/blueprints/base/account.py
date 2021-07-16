# -*- coding: utf-8 -*-

"""
Blueprint module to handle account routes.
"""

# Standard libraries import
import secrets
import logging
import datetime

# Application modules import
from blueprints import application
from blueprints.base import blueprint
from blueprints.__locale__ import __
from plugins.identica import Plugin as IdenticaPlugin
from models.process_store import ProcessStore
from models.user_store import UserStore
from models.name_store import NameStore
from models.entity.user import User
from config import CONFIG

# Additional libraries import
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import AnonymousUserMixin
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SelectField
from wtforms import SubmitField
from wtforms import validators

# Constants
PROFILE_TEMPLATE = 'EVENT: %s'
LINK_TEMPLATE = 'https://t.me/user?id=%s'


class GlobalUser():
	"""
	"""
	__admin_uid_list = None

	@staticmethod
	def get_or_create_admin_uid_list() -> list:
		if GlobalUser.__admin_uid_list is None:
			GlobalUser.__admin_uid_list = []
			for from_id in CONFIG['admin']:
				user = UserStore.get_by_from_id(from_id)
				if user is not None:
					GlobalUser.__admin_uid_list += [ user.uid ]
		return GlobalUser.__admin_uid_list

	def get_admin_uid_list(self) -> list:
		return GlobalUser.get_or_create_admin_uid_list()


class SignedInUser(UserMixin, GlobalUser):
	"""
	This is a SignedInUser class to handle data of authenticated user.
	"""

	def __init__(self, user):
		super().__init__()
		self.user = user

	def get_id(self):
		"""
		Return uid for linked to SignedInUser object User entity.
		"""
		if self.user is not None:
			return self.user.uid

	def get_token(self):
		"""
		Return None for SignedInUser object (no anonymous token).
		"""
		return None

	def get_name(self):
		"""
		Return name object from session.
		"""
		if session.get('name') is not None:
			name = NameStore.read(session['name'])
			return name \
				if name is not None and name.user_id == self.user.id else None


class AnonymousUser(AnonymousUserMixin, GlobalUser):
	"""
	This is a AnonymousUser class to handle data of anonymous user.
	"""

	def get_id(self):
		"""
		Return None for AnonymousUser object (no user uid).
		"""
		return None

	def get_token(self):
		"""
		Return anonymous token for anonymous user.
		"""
		anonymous_token = session.get('anonymous_token')
		if anonymous_token is None:
			anonymous_token = secrets.token_hex(256)
			session['anonymous_token'] = anonymous_token
		return anonymous_token

	def get_name(self):
		"""
		Return None for AnonymousUser object (no name).
		"""
		session['name'] = None
		return None


# Initiate login manager
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'base.sign_in'
login_manager.anonymous_user = AnonymousUser
login_manager.session_protection = 'strong'


@login_manager.user_loader
def load_user(user_id):
	"""
	Return SignedInUser object linked to User entity by uid.
	"""
	return SignedInUser(UserStore.read(user_id))


class SignInForm(FlaskForm):
	"""
	This is a SignInForm class to retrieve form data.
	"""
	pin = StringField('signInPin')
	password = StringField('signInPassword')
	submit = SubmitField('signInSubmit')

	def __init__(self) -> "SignInForm":
		"""
		Initiate object with values from request.
		"""
		super(SignInForm, self).__init__()
		for field in self:
			if field.name != 'csrf_token':
				data = request.form.get(field.label.text)
				field.data = data if data is not None and len(data) > 0 else None


@blueprint.route('/account/sign-in/', methods=('GET', 'POST'))
def sign_in():
	"""
	Return sign-in page and login user on success.
	"""
	if current_user.is_authenticated:
		return redirect(url_for('base.get_home'))
	sign_in = SignInForm()
	if sign_in.validate_on_submit():
		if sign_in.pin.data is None:
			sign_in.pin.errors = [ __('Empty PIN') ]
		else:
			if sign_in.password.data is None:
				password = IdenticaPlugin.get_password(sign_in.pin.data)
				if password is None:
					logging.debug('Wrong PIN submitted')
					sign_in.pin.data = ''
					sign_in.pin.errors = [ __('Wrong PIN') ]
				else:
					sign_in.password.data = password
			else:
				verify_data = IdenticaPlugin.verify_pin(sign_in.pin.data)
				if verify_data is None:
					logging.debug('Wrong password submitted')
					return { 'redirect': url_for('base.sign_in') }
				elif verify_data.get('from'):
					user = UserStore().get_or_create_user(
						verify_data['from']['id'],
						'%s %s [%s]' % (
							verify_data['from'].get('first_name'),
							verify_data['from'].get('last_name'),
							verify_data['from'].get('username')
						)
					)
					ProcessStore.bind_token(user.uid, current_user.get_token())
					login_user(SignedInUser(user), remember=True)
					user_info = '%s (%s)' % \
						(
							user.name, user.from_id
						) if user is not None else None
					logging.debug('Signed in as user %s' % user_info)
					return { 'redirect': url_for('base.get_home') }
				return { 'wait': True }
	return render_template(
		'base/sign_in.html',
		sign_in=sign_in
	)


@blueprint.route('/account/identica/<url_token>/', methods=('GET',))
def authenticate_identica(url_token: str):
	"""
	Verify token and login user on success.
	"""
	if current_user.is_authenticated:
		return redirect(url_for('base.get_landing'))
	verify_data = IdenticaPlugin.verify_url(url_token)
	if verify_data is None:
		logging.debug('Wrong TOKEN submitted')
	elif verify_data.get('from'):
		user = UserStore().get_or_create_user(
			verify_data['from']['id'],
			'%s %s [%s]' % (
				verify_data['from'].get('first_name'),
				verify_data['from'].get('last_name'),
				verify_data['from'].get('username')
			)
		)
		login_user(SignedInUser(user), remember=True)
		user_info = '%s (%s)' % \
			(
				user.name, user.from_id
			) if user is not None else None
		logging.debug('Signed in as user %s' % user_info)
	return redirect(url_for('base.get_landing'))


@blueprint.route('/account/sign-out/', methods=('GET',))
def sign_out():
	"""
	Return sign-in page and login user.
	"""
	if current_user.is_authenticated:
		logout_user()
	return redirect(url_for('base.get_home'))


@blueprint.route('/timezone/', methods=('POST',))
def set_timezone():
	"""
	Set timezone for session.
	"""
	try:
		session['timezone_offset'] = int(request.form.get('timezoneOffset'))
		utc_now = datetime.datetime.utcnow()
		return {
			'status': 'ok',
			'message': {
				'text': 'Timezone for session initiated successfully',
				'utc': utc_now,
				'local': utc_now - datetime.timedelta(minutes=session['timezone_offset'])
			}
		}
	except:
		pass
	return {
		'status': 'error',
		'message': {
			'text': 'Timezone initiation error'
		}
	}


@blueprint.route('/feedback/', methods=('POST',))
def send_feedback():
	"""
	Send feedback.
	"""
	IdenticaPlugin.notify_user(
		CONFIG['feedback'],
		'ID: %s\nName: %s\nContact: %s\nMessage: %s' % (
			current_user.user.from_id \
				if current_user.is_authenticated else 'anonymous',
			request.form.get('feedbackerName'),
			request.form.get('feedbackerContact'),
			request.form.get('feedbackerMessage')
		)
	)
	return {
		'redirect': None,
		'message': __('Thank you for your feedback!')
	}
