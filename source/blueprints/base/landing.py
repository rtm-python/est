# -*- coding: utf-8 -*-

"""
Blueprint module to handle landing routes.
"""

# Standard libraries import


# Application modules import
from blueprints import application
from blueprints.base import blueprint


@blueprint.route('/', methods=('GET',))
@blueprint.route('/landing/', methods=('GET',))
def get_landing():
	"""
	Return landing page.
	"""
	return 'Landing Page', 200
