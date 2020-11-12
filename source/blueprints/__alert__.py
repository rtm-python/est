# -*- coding: utf-8 -*-

"""
Helper module to handle alert.
"""

# Standard libraries import
from enum import Enum

# Additional libraries import
from flask import request
from blueprints.__args__ import get_integer
from blueprints.__args__ import set_value


class AlertType(Enum):
	"""
	This is an enumeration class for alert types.
	"""
	DANGER = 'danger'
	DARK = 'dark'
	SUCCESS = 'success'


class AlertButton():
	"""
	This is an alert button class.
	"""

	def __init__(self, type: AlertType, link: str, label: str) -> 'AlertButton':
		"""
		Initiate AlertButton object.
		"""
		self.type = type
		self.link = link
		self.label = label


class Alert():
	"""
	This is an alert class.
	"""

	def __init__(self, title: str, message_text: str,
							 message_args: tuple, buttons: [AlertButton]
							 ) -> 'Alert':
		"""
		Inititate Alert object.
		"""
		self.title = title
		self.message_text = message_text
		self.message_args = message_args
		self.buttons = buttons
