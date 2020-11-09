# -*- coding: utf-8 -*-

"""
Blueprint module to handle examination process routes.
"""

# Standard libraries import


# Application modules import
from blueprints import application
from blueprints.examination import blueprint


@blueprint.route('/process/', methods=('GET',))
def get_examination_process():
	"""
	Return examination process page.
	"""
	return 'Examination Process Page', 200
