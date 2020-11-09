# -*- coding: utf-8 -*-

"""
Blueprint module to handle examination results routes.
"""

# Standard libraries import


# Application modules import
from blueprints import application
from blueprints.statistics import blueprint


@blueprint.route('/', methods=('GET',))
@blueprint.route('/examination/', methods=('GET',))
def get_examination_results():
	"""
	Return examination results page.
	"""
	return 'Examination Results Page', 200
