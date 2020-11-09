# -*- coding: utf-8 -*-

"""
Initial blueprint module to initiate examination blueprint.
"""

# Standard libraries import
import os

# Application modules import
from blueprints import application

# Additional libraries import
from flask import Blueprint

# Initiate Blueprint object
blueprint = Blueprint(
	'examination', __name__,
	static_folder=os.path.join(
		os.path.abspath(os.curdir), 'source/static'),
	template_folder=os.path.join(
		os.path.abspath(os.curdir), 'source/templates')
)

# Routes import
from blueprints.examination import catalog
from blueprints.examination import process
