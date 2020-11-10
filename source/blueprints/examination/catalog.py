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
from blueprints.__locale__ import __

# Additional libraries import
from flask import render_template

# Test data
test_examinations = [
	{
		'uid': '1',
		'name': 'Test Examination 1',
		'description': 'Simple exmine for your kids',
		'plugin': 'arithmetics',
		'options': [],
		'created': datetime.datetime.utcnow(),
		'modified': datetime.datetime.utcnow(),
		'passed': datetime.datetime.utcnow(),
		'public': True,
		'score': 30
	},
	{
		'uid': '2',
		'name': 'Test Examination 2',
		'description': 'Simple exmine for your kids',
		'plugin': 'arithmetics',
		'options': [],
		'created': datetime.datetime.utcnow(),
		'modified': datetime.datetime.utcnow(),
		'passed': datetime.datetime.utcnow(),
		'public': True,
		'score': 30
	},
	{
		'uid': '3',
		'name': 'Test Examination 3',
		'description': 'Simple exmine for your kids',
		'plugin': 'arithmetics',
		'options': [],
		'created': datetime.datetime.utcnow(),
		'modified': datetime.datetime.utcnow(),
		'passed': datetime.datetime.utcnow(),
		'public': True,
		'score': 30
	}
]
#test_examinations += test_examinations
#test_examinations += test_examinations
#test_examinations += test_examinations
#test_examinations += test_examinations
#test_examinations += test_examinations


@blueprint.route('/', methods=('GET',))
@blueprint.route('/catalog/', methods=('GET',))
def get_examination_catalog():
	"""
	Return examination catalog page.
	"""
	pagination = get_pagination(len(test_examinations))
	pagination['endpoint'] = 'examination.get_examination_catalog'
	examinations = test_examinations[
		(pagination['page_index'] - 1) * pagination['per_page']:
		pagination['page_index'] * pagination['per_page']
	]
	caption = __('%d examinations out of %d') % \
		(
			min(pagination['entity_count'], pagination['per_page']),
			pagination['entity_count']
		)
	return render_template(
		'examination/catalog.html',
		examinations=examinations,
		caption=caption,
		pagination=pagination
	)


@blueprint.route('/catalog/view/<uid>/', methods=('GET',))
def get_examination(uid: str):
	"""
	Return examination view page.
	"""
	return 'Examination View Page'


@blueprint.route('/catalog/edit/<uid>/', methods=('GET',))
def edit_examination(uid: str):
	"""
	Return examination edit page.
	"""
	return 'Examination Edit Page'


@blueprint.route('/catalog/delete/<uid>/', methods=('GET',))
def delete_examination(uid: str):
	"""
	Return examination delete page.
	"""
	return 'Examination Delete Page'
