# -*- coding: utf-8 -*-

"""
Blueprint module to handle sign routes.
"""

# Standard libraries import
import secrets

# Application modules import
from blueprints import application
from blueprints.base import blueprint

# Additional libraries import
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import AnonymousUserMixin
from flask import session


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
			return unicode(self.user.uid)

	def get_token():
		"""
		Return None for SignedInUser object (no anonymous token).
		"""
		return None


class AnonymousUser(AnonymousUserMixin):
	"""
	This is a AnonymousUser class to handle data of anonymous user.
	"""

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
	# TODO: Sign entity and return entity by uid
	return SignedInUser(None)


@blueprint.route('/sign/in/', methods=('GET',))
def sign_in():
	"""
	Return sign-in  page.
	"""
	return 'Sign-In Page', 200


@blueprint.route('/sign/up/', methods=('GET',))
def sign_up():
	"""
	Return sign-up  page.
	"""
	return 'Sign-Up Page', 200


@blueprint.route('/sign/out/', methods=('GET',))
def sign_out():
	"""
	Return sign-out  page.
	"""
	return 'Sign-Out Page', 200
