# -*- coding: utf-8 -*-

"""
Blueprint module to handle account routes.
"""

# Standard libraries import
import secrets
import logging

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
FEEDBACK_TEMPLATE = '%s [%s]: %s'
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


class ProfilerForm(FlaskForm):
	"""
	This is a ProfileForm class to retrieve form data.
	"""
	notification_profile = SelectField(
		'profilerNotificationProfile',
		validators=[validators.DataRequired()]
	)
	notification_test_start = SelectField(
		'profilerNotificationTestStart',
		validators=[validators.DataRequired()]
	)
	notification_test_complete = SelectField(
		'profilerNotificationTestComplete',
		validators=[validators.DataRequired()]
	)
	submit = SubmitField('profilerSubmit')

	def __init__(self, user: object = None) -> "ProfilerForm":
		"""
		Inititate object with choices.
		"""
		super(ProfilerForm, self).__init__()
		self.notification_profile.choices = [
			('yes', __('Send notification')),
			('no', __('Keep silence')),
		]
		self.notification_test_start.choices = [
			('yes', __('Send notification')),
			('no', __('Keep silence')),
		]
		self.notification_test_complete.choices = [
			('yes', __('Send notification')),
			('no', __('Keep silence')),
		]
		if user:
			self.notification_profile.data = 'yes' \
				if user.notification_profile else 'no'
			self.notification_test_start.data = 'yes' \
				if user.notification_test_start else 'no'
			self.notification_test_complete.data = 'yes' \
				if user.notification_test_complete else 'no'
		else:
			for field in self:
				if field.name != 'csrf_token':
					field.data = request.form.get(field.label.text)


class FeedbackerForm(FlaskForm):
	"""
	This is a FeedbackForm class to retrieve form data.
	"""
	message = StringField(
		'feedbackerMessage',
		validators=[validators.DataRequired()]
	)
	submit = SubmitField('feedbackerSubmit')

	def __init__(self, post: bool) -> "ProfilerForm":
		"""
		Inititate object with choices.
		"""
		super(FeedbackerForm, self).__init__()
		if post:
			for field in self:
				if field.name != 'csrf_token':
					field.data = request.form.get(field.label.text)


@blueprint.route('/account/', methods=('GET', 'POST'))
@blueprint.route('/account/profile/', methods=('GET', 'POST'))
def get_profile():
	"""
	Return profile page.
	"""
	if not current_user.is_authenticated:
		return redirect(url_for('base.sign_in'))
	if request.method == 'GET':
		profiler = ProfilerForm(current_user.user)
	else:
		if current_user.user.notification_profile:
			IdenticaPlugin.notify_user(
				current_user.user.from_id,
				PROFILE_TEMPLATE % __('Profile updated')
			)
		profiler = ProfilerForm()
	if request.form.get('profilerSubmit') and \
			profiler.validate_on_submit(): # Valid post request
		UserStore.update_notifications(
			current_user.user.uid,
			profiler.notification_profile.data == 'yes',
			profiler.notification_test_start.data == 'yes',
			profiler.notification_test_complete.data == 'yes'
		)
	feedbacker = FeedbackerForm(request.method == 'POST')
	if request.form.get('feedbackerSubmit') and \
			 feedbacker.validate_on_submit(): # Valid post request
		IdenticaPlugin.notify_user(
			current_user.user.from_id,
			__('Thank you for your feedback!')
		)
		IdenticaPlugin.notify_user(
			CONFIG['feedback'],
			FEEDBACK_TEMPLATE % (
				LINK_TEMPLATE % current_user.user.from_id,
				current_user.user.name, feedbacker.message.data[:100]
			)
		)
		return redirect(url_for('base.get_profile'))
	return render_template(
		'base/profile.html',
		profiler=profiler,
		feedbacker=feedbacker,
		nav_active='account'
	)


@blueprint.route('/account/sign-in/', methods=('GET', 'POST'))
def sign_in():
	"""
	Return sign-in page and login user.
	"""
	if current_user.is_authenticated:
		return redirect(url_for('base.get_landing'))
	sign_in = SignInForm()
	if sign_in.validate_on_submit() and sign_in.pin.data is not None:
		if sign_in.password.data is None:
			password = IdenticaPlugin.get_password(sign_in.pin.data)
			if password is None:
				logging.debug('Wrong password submitted')
				return redirect(url_for('base.sign_in'))
			sign_in.password.data = password
		else:
			verify_data = IdenticaPlugin.verify_pin(sign_in.pin.data)
			if verify_data is None:
				logging.debug('Wrong PIN submitted')
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
				login_user(SignedInUser(user), remember=True)
				user_info = '%s (%s / %s)' % \
					(
						' '.join([str(user.first_name), str(user.last_name)]),
						user.from_id, user.username
					) if user is not None else None
				logging.debug('Sign in as user %s' % user_info)
				return { 'redirect': url_for('base.get_landing') }
			return { 'wait': True }
	return render_template(
		'base/sign_in.html',
		sign_in=sign_in,
		nav_active='account'
	)


@blueprint.route('/account/sign-out/', methods=('GET',))
def sign_out():
	"""
	Return sign-in page and login user.
	"""
	if current_user.is_authenticated:
		logout_user()
	return redirect(url_for('base.get_profile'))
