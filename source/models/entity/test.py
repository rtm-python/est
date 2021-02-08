# -*- coding: utf-8 -*-

'''
Entity module for test entity.
'''

# Additional libraries import
from sqlalchemy import Column
from sqlalchemy import ForeignKey

# Project modules imports
from models import database
from models.entity.__base__ import Entity


class Test(Entity):
	'''
	This is a class for Test entity.
	'''
	__tablename__ = 'test'
	name = Column(database.String, index=True, nullable=False)
	plugin = Column(database.String, index=True, nullable=False)
	plugin_options = Column(database.String, index=True, nullable=False)
	repeat = Column(database.Integer, index=True, nullable=False)
	speed = Column(database.Integer, index=True, nullable=False)

	def __init__(self, name: str, plugin: str, plugin_options: str,
							 repeat: int, speed: int) -> "Test":
		'''
		Initiate object and stores Test's data.
		'''
		super().__init__()
		self.name = name
		self.plugin = plugin
		self.plugin_options = plugin_options
		self.repeat = repeat
		self.speed = speed
