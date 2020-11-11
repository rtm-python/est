# -*- coding: utf-8 -*-

"""
Helper  module to handle arguments..
"""

# Standard libraries import


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
		print(args)
		value = args.get(name)
		if value is not None:
			try:
				return value == 'true' or value == 'True' or value is True
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
