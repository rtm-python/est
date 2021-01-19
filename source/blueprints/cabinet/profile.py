# -*- coding: utf-8 -*-

"""
Blueprint module to handle profile routes.
"""

# Standard libraries import


# Application modules import
from blueprints import application
from blueprints.cabinet import blueprint

# Additional libraries import
from flask import render_template

@blueprint.route('/', methods=('GET',))
@blueprint.route('/profile/', methods=('GET',))
def get_profile():
	"""
	Return profile page.
	"""
	return render_template('cabinet/profile.html')
