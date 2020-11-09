# -*- coding: utf-8 -*-

"""
Initial blueprint module to initiate examination blueprint.
"""

# Standard libraries import


# Application modules import
from blueprints import application

# Additional libraries import
from flask import Blueprint

# Initiate Blueprint object
blueprint = Blueprint(
	'examination', __name__,
	static_folder='',
	template_folder=''
)

# Routes import
from blueprints.examination import catalog
from blueprints.examination import process
