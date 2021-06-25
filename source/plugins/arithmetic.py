# -*- coding: utf-8 -*-

"""
Plugin module to handle examination process.
"""

# Standard libraries import
import json
from random import randint

# Performance constants
ADDITION_TIME_PER_BIT = 1.5
SUBSTRACTION_TIME_PER_BIT = 2.5
MULTIPLICATION_TIME_PER_BIT = 1
DIVISION_TIME_PER_BIT = 1

# Plugin options
options = [
	{
		'name':	'max_limit',
		'label': {'text': 'maxLimit'},
		'description': 'Maximum limit',
		'choices': [
			('10', '10'),	('20', '20'),	('30', '30'),	('40', '40'),	('50', '50'),
			('100', '100'),	('500', '500'),	('1000', '1000'),	('5000', '5000'),
			('10000', '10000'),	('100000', '100000'),	('1000000', '1000000')
		]
	},
	{
		'name':	'vars_count',
		'label': {'text': 'varsCount'},
		'description': 'Number of variables',
		'choices': [('2', '2'), ('3', '3'), ('4', '4')]
	},
	{
		'name':	'result_only',
		'label': {'text': 'resultOnly'},
		'description': 'Only result is unknown',
		'choices': [('yes', 'Yes'), ('no', 'No')]
	},
	{
		'name':	'addition',
		'label': {'text': 'addition'},
		'description': 'Addition',
		'choices': [('use', 'Use'), ('skip', 'Skip')]
	},
	{
		'name':	'substraction',
		'label': {'text': 'substraction'},
		'description': 'Substraction',
		'choices': [('use', 'Use'), ('skip', 'Skip')]
	},
	{
		'name':	'multiplication',
		'label': {'text': 'multiplication'},
		'description': 'Multiplication',
		'choices': [('use', 'Use'), ('skip', 'Skip')]
	},
	{
		'name':	'division',
		'label': {'text': 'division'},
		'description': 'Division',
		'choices': [('use', 'Use'), ('skip', 'Skip')]
	}
]

# Map option name to valid data
valid_data_dict = {}
for option in options:
	valid_data_dict[option['name']] = \
		[choice[0] for choice in option['choices']]


def get_valid_value(request_form, label_text: str, name: str) -> str:
	"""
	Validate and return value from request form.
	"""
	value = request_form.get(label_text)
	if value in valid_data_dict[name]:
		return value
	raise ValueError('Not valid data.')


def parse_options(request_form, indent=None) -> str:
	"""
	Return text string representation of options dictionary.
	"""
	return json.dumps(
		{
			'max_limit': get_valid_value(request_form, 'maxLimit', 'max_limit'),
			'vars_count': get_valid_value(request_form, 'varsCount', 'vars_count'),
			'result_only': get_valid_value(request_form, 'resultOnly', 'result_only'),
			'addition': get_valid_value(request_form, 'addition', 'addition'),
			'substraction': get_valid_value(request_form, 'substraction', 'substraction'),
			'multiplication': get_valid_value(request_form, 'multiplication', 'multiplication'),
			'division': get_valid_value(request_form, 'division', 'division')
		},
		indent=indent
	)


def form_options(values: str, validate: bool=False) -> dict:
	"""
	Return options with defined values.
	"""
	try:
		values_dict = json.loads(values)
		if validate:
			if values_dict['addition'] == 'skip' and \
					values_dict['substraction'] == 'skip' and \
					values_dict['multiplication'] == 'skip' and \
					values_dict['division'] == 'skip':
				raise ValueError()
			max_limit = int(values_dict['max_limit'])
			vars_count = int(values_dict['vars_count'])
	except:
		if validate:
			raise ValueError()
		values_dict = {}
	result = []
	for option in options:
		option['data'] = values_dict.get(option['name'], '')
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
	if options['addition'] == 'use':
		operations += [get_addition]
	if options['substraction'] == 'use':
		operations += [get_substraction]
	if options['multiplication'] == 'use':
		operations += [get_multiplication]
	if options['division'] == 'use':
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
		preset = operation(int(options['max_limit']), preset)
	# Calculate performance for preset
	speed_time = 0
	for var in preset[1:]:
		speed_time += len(var)
	if operation is get_addition:
		speed_time *= ADDITION_TIME_PER_BIT
	if operation is get_substraction:
		speed_time *= SUBSTRACTION_TIME_PER_BIT
	if operation is get_multiplication:
		speed_time *= MULTIPLICATION_TIME_PER_BIT
	if operation is get_division:
		speed_time *= DIVISION_TIME_PER_BIT
	# Replace one of the vars with question mark
	hide_index = randint(1, len(preset) - 1) \
		if options['result_only'] == 'false' else len(preset) - 1
	if preset[0] in ['x', '/']:
		if preset[hide_index] != 0 and '0' in preset:
			hide_index = len(preset) - 1
	if hide_index < len(preset) - 1:
		speed_time *= 1.05
	# Prepare data
	answer = preset[hide_index]
	preset[hide_index] = '?'
	return {
		'task': '%s = %s' % \
			((' %s ' % preset[0]).join(preset[1: -1]), preset[-1]),
		'answer': answer,
		'speed_time': int(speed_time)
	}
