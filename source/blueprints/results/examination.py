# -*- coding: utf-8 -*-

"""
Blueprint module to handle examination results routes.
"""

# Standard libraries import


# Application modules import
from blueprints import application
from blueprints.results import blueprint


@blueprint.route('/', methods=('GET',))
@blueprint.route('/top/', methods=('GET',))
def get_top():
	"""
	Return examination top results page.
	"""
	return 'Examination Top Results Page', 200
