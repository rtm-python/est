# -*- coding: utf-8 -*-

"""
Initial blueprint module to initiate cabinet blueprint.
"""

# Standard libraries import


# Application modules import
from blueprints import application

# Additional libraries import
from flask import Blueprint

# Initiate Blueprint object
blueprint = Blueprint(
	'cabinet', __name__,
	static_folder='',
	template_folder=''
)

# Routes import
from blueprints.cabinet import profile
