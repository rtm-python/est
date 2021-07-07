# -*- coding: utf-8 -*-

"""
Time plugin module to handle examination process.
"""

# Standard libraries import
import json
from random import randint

# Performance constants
DEFINITION_TIME_PER_TASK = 3.0
CALCULATION_TIME_PER_TASK = 9.0

# Default constants
MAX_MINUTES = 24 * 60

# Plugin options
options = [
	{
		'name':	'difficulty',
		'label': {'text': 'difficulty'},
		'description': 'Difficulty',
		'choices': [
			('easy', 'Easy'), ('normal', 'Normal'), ('hard', 'Hard')
		]
	},
	{
		'name':	'definition',
		'label': {'text': 'definition'},
		'description': 'Definition',
		'choices': [('use', 'Use'), ('skip', 'Skip')]
	},
	{
		'name':	'calculation',
		'label': {'text': 'calculation'},
		'description': 'Calculation',
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
			'difficulty': get_valid_value(request_form, 'difficulty', 'difficulty'),
			'definition': get_valid_value(request_form, 'definition', 'definition'),
			'calculation': get_valid_value(request_form, 'calculation', 'calculation')
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
			if values_dict['definition'] == 'skip' and \
					values_dict['calculation'] == 'skip':
				raise ValueError()
	except:
		if validate:
			raise ValueError()
		values_dict = {}
	result = []
	for option in options:
		option['data'] = values_dict.get(option['name'], '')
		result += [option]
	return result


def validate_answer(form) -> tuple:
	"""
	Return answer and errors list on invalid answer.
	"""
	hours = form.get('hours')
	minutes = form.get('minutes')
	try:
		if hours is not None and minutes is not None:
			return ('%02d:%02d' % (int(hours), int(minutes)), None)
		else:
			return (None, ['Answer should be in form hh:mm.'])
	except:
		return (None, ['Answer should be in form hh:mm.'])


def get_random_operation(options: dict) -> list:
	"""
	Return random accessible operation.
	"""
	operations = []
	if options['definition'] == 'use':
		operations += [get_definition]
	if options['calculation'] == 'use':
		operations += [get_calculation]
	return operations[randint(0, len(operations) - 1)]


def round_minutes(minutes: int, multiplicity: int) -> int:
	"""
	Return rounded minutes according to multiplicity value.
	"""
	return int(minutes / multiplicity) * multiplicity


def get_definition(multiplicity: int) -> (tuple, tuple, int):
	"""
	Return values and result for definition.
	"""
	minutes = randint(0, MAX_MINUTES)
	hours = int(minutes / 60)
	minutes = round_minutes(minutes - hours * 60, multiplicity)
	return ((hours, minutes), None, '%02d:%02d' % (hours, minutes))


def get_calculation(multiplicity: int) -> (tuple, tuple, int):
	"""
	Return values and result for calculation.
	"""
	minutes = randint(0, MAX_MINUTES - 60)
	hours = int(minutes / 60)
	minutes = round_minutes(minutes - hours * 60, multiplicity)
	next_minutes = randint(hours * 60 + minutes, MAX_MINUTES)
	next_hours = int(next_minutes / 60)
	next_minutes = \
		round_minutes(next_minutes - next_hours * 60, multiplicity)
	diff_minutes = (next_hours * 60 + next_minutes) - (hours * 60 + minutes)
	diff_hours = int(diff_minutes / 60)
	diff_minutes = diff_minutes - diff_hours * 60
	return (
		(hours, minutes),
		(next_hours, next_minutes),
		'%02d:%02d' % (diff_hours, diff_minutes)
	)


def get_data(options: dict) -> dict:
	"""
	Return data dictionary.
	"""
	if options['difficulty'] == 'easy':
		multiplicity = 15
	elif options['difficulty'] == 'normal':
		multiplicity = 10
	else:
		multiplicity = 5
	operation = get_random_operation(options)
	source_hours_minutes, next_hours_minutes, answer = \
		operation(multiplicity)
	# Calculate performance
	if operation is get_definition:
		limit_time = DEFINITION_TIME_PER_TASK
	if operation is get_calculation:
		limit_time = CALCULATION_TIME_PER_TASK
	# Prepare data
	return {
		'task': (source_hours_minutes, next_hours_minutes),
		'answer': answer,
		'limit_time': int(limit_time)
	}
