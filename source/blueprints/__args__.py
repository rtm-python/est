# -*- coding: utf-8 -*-

"""
Helper module to handle arguments.
"""

# Standard libraries import
import string

# Application modules import


# Additional libraries import
from flask import request
from flask import session


def get_integer(name: str, default: int = None) -> int:
	"""
	Return integer value by name from user's request or session.
	"""
	for args in [request.args, session.get('args') or {}]:
		value = args.get(name)
		if value is not None:
			try:
				return int(value)
			except:
				pass
	return default


def get_string(name: str, default: str = None) -> str:
	"""
	Return string value by name from user's request or session.
	"""
	for args in [request.args, session.get('args') or {}]:
		value = args.get(name)
		if value is not None:
			try:
				return str(value)
			except:
				pass
	return default


def get_boolean(name: str, default: bool = None) -> bool:
	"""
	Return boolean value by name from user's request or session.
	"""
	for args in [request.args, session.get('args') or {}]:
		value = args.get(name)
		if value is not None:
			try:
				return value == 'true' or value == 'True' or \
					value == 'on' or value is True
			except:
				pass
	return default


def set_value(name: str, value: int) -> None:
	"""
	Set name, value pair to session args dictionary.
	"""
	args = session.get('args')
	if args is None:
		args = {}
	args[name] = value
	session['args'] = args


def convert_name_to_underlined(name_camel_case: str) -> str:
	"""
	Return name in camelCase to underlined.
	"""
	for letter in string.ascii_uppercase:
		if letter in name_camel_case:
			name_parts = []
			index = 0
			for part in name_camel_case.split(letter):
				if index == 0:
					name_parts += [part]
					index += len(part)
				else:
					name_parts += [name_camel_case[index].lower() + part]
					index += len(part) + 1
			name_camel_case = '_'.join(name_parts)
	return name_camel_case


def convert_name_to_camel_case(name_underlined: str) -> str:
	"""
	Return name in underlined to camelCase
	"""
	name_parts = []
	for part in name_underlined.split('_'):
		if len(name_parts) == 0:
			name_parts += [part]
		else:
			name_parts += [part[0].upper() + part[1:]]
	return ''.join(name_parts)
