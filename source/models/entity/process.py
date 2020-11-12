# -*- coding: utf-8 -*-

'''
Entity module for process entity.
'''

# Additional libraries import
from sqlalchemy import Column
from sqlalchemy import ForeignKey

# Project modules imports
from models import database
from models.entity.__base__ import Entity


class Process(Entity):
	'''
	This is a class for Process entity.
	'''
	__tablename__ = 'process'
	examination_id = Column(
		database.Integer, ForeignKey('examination.id'),
		index=True, nullable=False
	)
	plugin = Column(database.String, index=True, nullable=False)
	plugin_options = Column(database.String, index=True, nullable=False)
	name = Column(database.String, index=True, nullable=False)
	repeat = Column(database.Integer, index=True, nullable=False)
	performance = Column(database.Integer, index=True, nullable=False)
	answered_count = Column(
		database.Integer, default=0,
		index=True, nullable=False
	)
	correct_count = Column(
		database.Integer, default=0,
		index=True, nullable=False
	)

	def __init__(self, examination_id: int,
							 plugin: str, plugin_options: str,
							 name: str, repeat: int, performance: int
							 ) -> "Process":
		'''
		Initiate object and stores Process' data.
		'''
		super().__init__()
		self.examination_id = examination_id
		self.plugin = plugin
		self.plugin_options = plugin_options
		self.name = name
		self.repeat = repeat
		self.performance = performance
