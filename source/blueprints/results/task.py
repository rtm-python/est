# -*- coding: utf-8 -*-

"""
Blueprint module to handle completed task routes.
"""

# Standard libraries import


# Application modules import
from blueprints import application
from blueprints.results import blueprint


@blueprint.route('/task/', methods=('GET',))
def get_completed_tasks():
	"""
	Return completed tasks page.
	"""
	return 'Completed Tasks Page', 200
