# -*- coding: utf-8 -*-

"""
Blueprint module to handle examination catalog routes.
"""

# Standard libraries import
import datetime

# Application modules import
from blueprints import application
from blueprints.examination import blueprint

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


@blueprint.route('/', methods=('GET',))
@blueprint.route('/catalog/', methods=('GET',))
def get_examination_catalog():
	"""
	Return examination catalog page.
	"""
	examinations = test_examinations
	pages = ['1', '2', '3']
	return render_template(
		'examination/catalog.html',
		examinations=examinations,
		pages=pages
	)
