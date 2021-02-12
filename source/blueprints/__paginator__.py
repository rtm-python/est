# -*- coding: utf-8 -*-

"""
Helper module to handle pagination.
"""

# Additional libraries import
from flask import request
from blueprints.__args__ import get_integer
from blueprints.__args__ import set_value


def get_pagination(prefix: str, entity_count: int,
									 default_per_page: int = 12) -> dict:
	"""
	Return dictionary with page_index, per_page, page_count
	and entity_count values.
	"""
	# Set prefix names
	prefix_page_index = '%sPageIndex' % prefix
	prefix_per_page = '%sPerPage' % prefix
	# Get page_index and per_page from request
	page_index = get_integer(prefix_page_index, 1)
	per_page = get_integer(prefix_per_page, 12)
	# Calculate page_count
	page_count = entity_count / per_page
	page_count = int(page_count) + 1 \
		if int(page_count) < page_count else int(page_count)
	# Check page_index and per_page validity
	if (page_index < 1 or page_index > page_count) and page_index != 1:
		raise ValueError('Requested page_index out of range!')
	if per_page < 1:
		raise ValueError('Requested per_page out of range!')
	# Store arguments in session
	set_value(prefix_page_index, page_index)
	set_value(prefix_per_page, per_page)
	return {
		"page_index": page_index,
		"per_page": per_page,
		"page_count": page_count,
		"entity_count": entity_count
	}
