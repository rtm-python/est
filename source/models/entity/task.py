# -*- coding: utf-8 -*-

'''
Entity module for task entity.
'''

# Additional libraries import
from sqlalchemy import Column
from sqlalchemy import ForeignKey

# Project modules imports
from models import database
from models.entity.__base__ import Entity


class Task(Entity):
	'''
	This is a class for Task entity.
	'''
	__tablename__ = 'task'
	process_id = Column(
		database.Integer, ForeignKey('process.id'),
		index=True, nullable=False
	)
	data = Column(database.String, index=True, nullable=False)
	answer = Column(database.String, index=True, nullable=True)
	correct_answer = Column(database.Boolean, index=True, nullable=True)

	def __init__(self, process_id: int, data: str) -> "Task":
		'''
		Initiate object and stores Task's data.
		'''
		super().__init__()
		self.process_id = process_id
		self.data = data
