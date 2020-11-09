# -*- coding: utf-8 -*-

"""
Blueprint module to handle examination catalog routes.
"""

# Standard libraries import


# Application modules import
from blueprints import application
from blueprints.examination import blueprint


@blueprint.route('/', methods=('GET',))
@blueprint.route('/catalog/', methods=('GET',))
def get_examination_catalog():
	"""
	Return examination catalog page.
	"""
	return 'Examination Catalog Page', 200
