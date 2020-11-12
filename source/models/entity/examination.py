# -*- coding: utf-8 -*-

'''
Entity module for examination entity.
'''

# Standard libraries import


# Additional libraries import
from sqlalchemy import Column
from sqlalchemy import ForeignKey

# Project modules imports
from models import database
from models.entity.__base__ import Entity


class Examination(Entity):
	'''
	This is a class for Examination entity.
	'''
	__tablename__ = 'examination'
	name = Column(database.String, index=True, nullable=False)
	description = Column(database.String, index=True, nullable=False)
	plugin = Column(database.String, index=True, nullable=False)
	plugin_options = Column(database.String, index=True, nullable=False)
	default_repeat = Column(database.Integer, index=True, nullable=False)
	default_performance = Column(database.Integer, index=True, nullable=False)

	def __init__(self, name: str, description: str,
							 plugin: str, plugin_options: str,
							 default_repeat: int, default_performance: int
							 ) -> "Examination":
		'''
		Initiate object and stores Examination's data.
		'''
		super().__init__()
		self.name = name
		self.description = description
		self.plugin = plugin
		self.plugin_options = plugin_options
		self.default_repeat = default_repeat
		self.default_performance = default_performance
