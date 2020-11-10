# -*- coding: utf-8 -*-

"""
Helper module to handle pagination.
"""

# Additional libraries import
from flask import request


def get_pagination(entity_count: int) -> dict:
	"""
	Return dictionary with page_index, per_page, page_count
	and entity_count values.
	"""
	# get page_index and per_page from request
	page_index = request.args.get('page_index') or 1
	page_index = int(page_index)
	per_page = request.args.get('per_page') or 10
	per_page = int(per_page)
	# calculate page_count
	page_count = entity_count / per_page
	page_count = int(page_count) + 1 \
		if int(page_count) < page_count else int(page_count)
	# check page_index and per_page validity
	if page_index < 1 or page_index > page_count:
		raise ValueError('Requested page_index out of range!')
	if per_page < 1:
		raise ValueError('Requested per_page out of range!')
	return {
		"page_index": page_index,
		"per_page": per_page,
		"page_count": page_count,
		"entity_count": entity_count
	}
