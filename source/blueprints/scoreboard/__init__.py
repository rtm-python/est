# -*- coding: utf-8 -*-

"""
Initial blueprint module to initiate scoreboard blueprint.
"""

# Standard libraries import

# Application modules import
from blueprints import application

# Additional libraries import
from flask import Blueprint

# Initiate Blueprint object
blueprint = Blueprint(
	'scoreboard', __name__,
	static_folder='',
	template_folder=''
)

# Routes import
from blueprints.scoreboard import chart
