# -*- coding: utf-8 -*-

"""
Helper module to handle pagination.
"""

# Additional libraries import
from flask import request
from blueprints.__args__ import get_integer
from blueprints.__args__ import set_value


def get_pagination(entity_count: int) -> dict:
	"""
	Return dictionary with page_index, per_page, page_count
	and entity_count values.
	"""
	# get page_index and per_page from request
	page_index = get_integer('page_index', 1)
	per_page = get_integer('per_page', 10)
	# calculate page_count
	page_count = entity_count / per_page
	page_count = int(page_count) + 1 \
		if int(page_count) < page_count else int(page_count)
	# check page_index and per_page validity
	if page_index < 1 or page_index > page_count:
		raise ValueError('Requested page_index out of range!')
	if per_page < 1:
		raise ValueError('Requested per_page out of range!')
	# Store arguments in session
	set_value('page_index', page_index)
	set_value('per_page', per_page)
	return {
		"page_index": page_index,
		"per_page": per_page,
		"page_count": page_count,
		"entity_count": entity_count
	}
