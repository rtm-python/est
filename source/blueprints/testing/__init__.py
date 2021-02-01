# -*- coding: utf-8 -*-

"""
Initial blueprint module to initiate testing blueprint.
"""

# Standard libraries import

# Application modules import
from blueprints import application

# Additional libraries import
from flask import Blueprint

# Initiate Blueprint object
blueprint = Blueprint(
	'testing', __name__,
	static_folder='',
	template_folder=''
)

# Routes import
from blueprints.testing import catalog
#from blueprints.examination import process
