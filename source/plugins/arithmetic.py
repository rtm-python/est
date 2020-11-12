# -*- coding: utf-8 -*-

"""
Plugin module to handle examination process.
"""

# Standard libraries import
import json

# Plugin options
options = [
	{
		'name':	'add',
		'label': 'Additions',
		'width': 2,
		'type': 'bool'
	},
	{
		'name':	'subs',
		'label': 'Substractions',
		'width': 2,
		'type': 'bool'
	},
	{
		'name':	'mult',
		'label': 'Multiplications',
		'width': 2,
		'type': 'bool'
	},
	{
		'name':	'div',
		'label': 'Divisions',
		'width': 2,
		'type': 'bool'
	},
	{
		'name':	'vars_count',
		'label': 'Number of variables',
		'width': 2,
		'type': 'select',
		'data': [
			{
				'name': '2',
				'label': '2'
			},
			{
				'name': '3',
				'label': '3'
			},
			{
				'name': '4',
				'label': '4'
			}
		]
	},
	{
		'name':	'result_only',
		'label': 'Only result is unknown',
		'width': 2,
		'type': 'bool'
	}
]

# Map option name to valid data
valid_data_dict = {}
for option in options:
	data = []
	if option['type'] == 'select':
		for item in option['data']:
			data += [item['name']]
	elif option['type'] == 'bool':
		data += ['true', 'false']
	valid_data_dict[option['name']] = data


def get_valid_value(request_form, name: str) -> str:
	"""
	Validate and return value from request form.
	"""
	value = request_form['option_%s' % name]
	if value in valid_data_dict[name]:
		return value
	raise ValueError('Not valid data.')


def parse_options(request_form) -> str:
	"""
	Return text string representation of options dictionary.
	"""
	return json.dumps(
		{
			'add': get_valid_value(request_form, 'add'),
			'subs': get_valid_value(request_form, 'subs'),
			'mult': get_valid_value(request_form, 'mult'),
			'div': get_valid_value(request_form, 'div'),
			'vars_count': get_valid_value(request_form, 'vars_count'),
			'result_only': get_valid_value(request_form, 'result_only')
		},
		indent=2
	)


def form_options(values: str, is_mandatory: bool=False) -> dict:
	"""
	Return options with defined values.
	"""
	try:
		values_dict = json.loads(values)
		if is_mandatory:
			# Validate plugin values
			if values_dict['add'] == 'false' and values_dict['subs'] == 'false' and \
					values_dict['mult'] == 'false' and values_dict['div'] == 'false':
				raise ValueError()
	except:
		if is_mandatory:
			raise ValueError()
		values_dict = {}
	result = []
	for option in options:
		option['value'] = values_dict.get(option['name'], '')
		result += [option]
	return result
