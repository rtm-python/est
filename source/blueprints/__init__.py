# -*- coding: utf-8 -*-

"""
Initial blueprints module to define blueprints.
"""

# Standard libraries import
import secrets
import importlib

# Application modules import
from config import config
from config import UrlPrefix

# Additional libraries import
from flask import Flask
from flask import redirect
from flask import url_for
from flask_paranoid import Paranoid

# Initiate Flask object
application = Flask(
	config['name'],
	static_url_path='',
	static_folder='source/static',
	template_folder='source/template'
)
application.config['SECRET_KEY'] = secrets.token_hex(256)
paranoid = Paranoid(application)
paranoid.redirect_view = 'base.get_landing'

# Blueprint modules import and blueprints registration
# (prevent circular imports)
for module_name in \
		[
			'base',
			'cabinet',
			'results',
			'examination'
		]:
	module = importlib.import_module('blueprints.%s' % module_name)
	application.register_blueprint(
		module.blueprint,
		url_prefix=getattr(UrlPrefix, module_name).value
	)

# Helper modules import
# (prevent circular imports)
from blueprints import __locale__


@paranoid.on_invalid_session
def redirect_on_invalid_session():
	"""
	Return redirect on invalid session.
	"""
	return redirect(url_for('base.get_landing'))
