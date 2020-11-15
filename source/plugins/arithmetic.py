# -*- coding: utf-8 -*-

"""
Plugin module to handle examination process.
"""

# Standard libraries import
import json
from random import randint

# Performance constants
ADDITION_TIME_PER_BIT = 1
SUBSTRACTION_TIME_PER_BIT = 2
MULTIPLICATION_TIME_PER_BIT = 2
DIVISION_TIME_PER_BIT = 3

# Plugin options
options = [
	{
		'name':	'limit',
		'label': 'Maximum number limit',
		'width': 2,
		'type': 'select',
		'data': [
			{
				'value': '10',
				'label': '10'
			},
			{
				'value': '20',
				'label': '20'
			},
			{
				'value': '30',
				'label': '30'
			},
			{
				'value': '40',
				'label': '40'
			},
			{
				'value': '50',
				'label': '50'
			},
			{
				'value': '100',
				'label': '100'
			},
			{
				'value': '500',
				'label': '500'
			},
			{
				'value': '1000',
				'label': '1000'
			},
			{
				'value': '5000',
				'label': '5000'
			},
			{
				'value': '10000',
				'label': '10000'
			},
			{
				'value': '100000',
				'label': '100000'
			},
			{
				'value': '1000000',
				'label': '1000000'
			}
		]
	},
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
		'width': 1,
		'type': 'select',
		'data': [
			{
				'value': '2',
				'label': '2'
			},
			{
				'value': '3',
				'label': '3'
			},
			{
				'value': '4',
				'label': '4'
			}
		]
	},
	{
		'name':	'result_only',
		'label': 'Only result is unknown',
		'width': 1,
		'type': 'bool'
	}
]

# Map option name to valid data
valid_data_dict = {}
for option in options:
	data = []
	if option['type'] == 'select':
		for item in option['data']:
			data += [item['value']]
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
			'limit': get_valid_value(request_form, 'limit'),
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
			limit = int(values_dict['limit'])
			vars_count = int(values_dict['vars_count'])
			if not values_dict['result_only'] in ['false', 'true']:
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


def validate_answer(answer: str) -> list:
	"""
	Return errors list on invalid answer.
	"""
	try:
		answer_int = int(answer)
		return None
	except:
		return ['Answer should be a number.']


def get_random_operation(options: dict) -> list:
	"""
	Return random accessible operation.
	"""
	operations = []
	if options['add'] == 'true':
		operations += [get_addition]
	if options['subs'] == 'true':
		operations += [get_substraction]
	if options['mult'] == 'true':
		operations += [get_multiplication]
	if options['div'] == 'true':
		operations += [get_division]
	return operations[randint(0, len(operations) - 1)]


def get_addition(limit: int, preset: list = None) -> list:
	"""
	Return values and result for addition.
	"""
	value_1 = randint(0, limit) \
		if preset is None else int(preset[-1])
	value_2 = randint(0, limit - value_1)
	preset = ['+', str(value_1), str(value_2), str(value_1 + value_2)] \
		if preset is None else preset[:-1] + [str(value_2), str(value_1 + value_2)]
	return preset


def get_substraction(limit: int, preset: list = None) -> list:
	"""
	Return values and result for substraction.
	"""
	value_1 = randint(0, limit) \
		if preset is None else int(preset[-1])
	value_2 = randint(0, value_1)
	preset = ['-', str(value_1), str(value_2), str(value_1 - value_2)] \
		if preset is None else preset[:-1] + [str(value_2), str(value_1 - value_2)]
	return preset


def get_multiplication(limit: int, preset: list = None) -> list:
	"""
	Return values and result for multiplication.
	"""
	value_1 = randint(1, limit) \
		if preset is None else int(preset[-1])
	value_2 = randint(0, int(limit / value_1)) \
		if value_1 > 0 else 0
	preset = ['x', str(value_1), str(value_2), str(value_1 * value_2)] \
		if preset is None else preset[:-1] + [str(value_2), str(value_1 * value_2)]
	return preset


def get_division(limit: int, preset: list = None) -> list:
	"""
	Return values and result for division.
	"""
	value_2 = randint(1, limit) \
		if preset is None else int(preset[1])
	value_1 = randint(1, int(limit / value_2)) * value_2
	preset = ['/', str(value_1), str(value_2), str(int(value_1 / value_2))] \
		if preset is None else [preset[0]] + [str(value_1), str(int(value_1 / value_2))] + preset[2:]
	return preset


def get_data(options: dict) -> dict:
	"""
	Return data dictionary.
	"""
	operation = get_random_operation(options)
	preset = None
	for i in range(int(options['vars_count']) - 1):
		preset = operation(int(options['limit']), preset)
	# Calculate performance for preset
	performance_time = 0
	for var in preset[1:]:
		performance_time += len(var)
	if operation is get_addition:
		performance_time *= ADDITION_TIME_PER_BIT
	if operation is get_substraction:
		performance_time *= SUBSTRACTION_TIME_PER_BIT
	if operation is get_multiplication:
		performance_time *= MULTIPLICATION_TIME_PER_BIT
	if operation is get_division:
		performance_time *= DIVISION_TIME_PER_BIT
	# Replace one of the vars with question mark
	hide_index = randint(1, len(preset) - 1) \
		if options['result_only'] == 'false' else len(preset) - 1
	if preset[0] in ['x', '/']:
		if preset[hide_index] != 0 and '0' in preset:
			hide_index = len(preset) - 1
	if hide_index < len(preset) - 1:
		performance = int(performance * 1.05)
	# Prepare data
	answer = preset[hide_index]
	preset[hide_index] = '?'
	return {
		'task': '%s = %s' % \
			((' %s ' % preset[0]).join(preset[1: -1]), preset[-1]),
		'answer': answer,
		'performance_time': performance_time
	}
