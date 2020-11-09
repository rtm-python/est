# -*- coding: utf-8 -*-

"""
Blueprint module to handle sign routes.
"""

# Standard libraries import


# Application modules import
from blueprints import application
from blueprints.base import blueprint


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
