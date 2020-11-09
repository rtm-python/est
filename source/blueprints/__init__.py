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
from flask_paranoid import Paranoid

# Initiate Flask object
application = Flask(config['name'])
application.config['SECRET_KEY'] = secrets.token_hex(256)
paranoid = Paranoid(application)
paranoid.redirect_view = 'base.landing'

# Blueprint modules import and blueprints registration
# (prevent circular imports)
for module_name in \
		[
			'base',
			'statistics',
			'examination'
		]:
	module = importlib.import_module('blueprints.%s' % module_name)
	application.register_blueprint(
		module.blueprint,
		url_prefix=getattr(UrlPrefix, module_name).value
	)
