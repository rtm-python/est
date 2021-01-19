# -*- coding: utf-8 -*-

"""
Blueprint module to handle sign routes.
"""

# Standard libraries import
import secrets
import logging

# Application modules import
from blueprints import application
from blueprints.base import blueprint
from identica import telegram as bot
from models.process_store import ProcessStore
from models.user_store import UserStore
from models.entity.user import User

# Additional libraries import
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import AnonymousUserMixin
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms import validators


class SignedInUser(UserMixin):
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


class AnonymousUser(AnonymousUserMixin):
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
	This is a  SignInForm class to retrieve form data.
	"""
	usercode = StringField()
	passcode = StringField(validators=[validators.DataRequired()])
	submit = SubmitField()


@blueprint.route('/sign/in/', methods=('GET', 'POST'))
def sign_in():
	"""
	Return sign-in page and login user.
	"""
	# TODO: verify for signed in user
	sign_in = SignInForm()
	if sign_in.validate_on_submit():
		usercode_item = bot.verify_usercode(
			sign_in.usercode.data, sign_in.passcode.data.strip())
		if usercode_item is not None: # usercode/passcode is valid
			anonymous_token = current_user.get_token()
			user = UserStore.get_or_create_user(
				usercode_item['from_id'], usercode_item['name'])
			logging.debug('Sign in as user %s (%s)' % (user.name, user.from_id))
			login_user(SignedInUser(user))
			logging.debug(
				'Defined user (%s) and token (%s)' % \
				(current_user.get_id(), anonymous_token)
			)
			logging.debug(
				'Binding anonymous processes to user: %d binded' % \
				ProcessStore.bind_token(current_user.get_id(), anonymous_token)
			)
			return redirect(url_for('base.get_landing'))
		logging.warning('Invalid usercode/passcode pair')
		return redirect(url_for('base.sign_in'))
	sign_in.usercode.value = bot.create_usercode()
	return render_template(
		'base/sign_in.html',
		sign_in=sign_in
	)


@blueprint.route('/sign/out/', methods=('GET',))
def sign_out():
	"""
	Return sign-out  page.
	"""
	return 'Sign-Out Page', 200
