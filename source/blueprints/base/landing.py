# -*- coding: utf-8 -*-

"""
Blueprint module to handle landing routes.
"""

# Standard libraries import
import os

# Application modules import
from blueprints import application
from blueprints.base import blueprint
from config import INFO_TEMPLATE_LIST

# Additional libraries import
from flask import render_template


@blueprint.route('/landing/', methods=('GET',))
def get_landing():
	"""
	Return landing page.
	"""
	return render_template(
		'base/landing.html',
		info_templates = INFO_TEMPLATE_LIST
	)
