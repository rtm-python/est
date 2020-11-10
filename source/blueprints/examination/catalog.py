# -*- coding: utf-8 -*-

"""
Blueprint module to handle examination catalog routes.
"""

# Standard libraries import
import datetime

# Application modules import
from blueprints import application
from blueprints.examination import blueprint
from blueprints.__paginator__ import get_pagination

# Additional libraries import
from flask import render_template

# Test data
test_examinations = [
	{
		'name': 'Test Examination 1',
		'plugin': 'arithmetics',
		'options': [],
		'created': datetime.datetime.utcnow(),
		'modified': datetime.datetime.utcnow(),
		'public': True
	},
	{
		'name': 'Test Examination 2',
		'plugin': 'arithmetics',
		'options': [],
		'created': datetime.datetime.utcnow(),
		'modified': datetime.datetime.utcnow(),
		'public': True
	},
	{
		'name': 'Test Examination 3',
		'plugin': 'arithmetics',
		'options': [],
		'created': datetime.datetime.utcnow(),
		'modified': datetime.datetime.utcnow(),
		'public': True
	}
]
test_examinations += test_examinations
test_examinations += test_examinations
test_examinations += test_examinations
test_examinations += test_examinations
test_examinations += test_examinations


@blueprint.route('/', methods=('GET',))
@blueprint.route('/catalog/', methods=('GET',))
def get_examination_catalog():
	"""
	Return examination catalog page.
	"""
	pagination = get_pagination(len(test_examinations))
	examinations = test_examinations[
		(pagination['page_index'] - 1) * pagination['per_page']:
		pagination['page_index'] * pagination['per_page']
	]
	print(pagination)
	return render_template(
		'examination/catalog.html',
		examinations=examinations,
		pagination=pagination
	)
