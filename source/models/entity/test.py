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
	extension = Column(database.String, index=True, nullable=False)
	extension_options = Column(database.String, index=True, nullable=False)
	answer_count = Column(database.Integer, index=True, nullable=False)
	limit_time = Column(database.Integer, index=True, nullable=False)
	user_uid = Column(database.String, index=True, nullable=True)

	def __init__(self, name: str, extension: str, extension_options: str,
							 answer_count: int, limit_time: int, user_uid: str) -> "Test":
		'''
		Initiate object and stores Test's data.
		'''
		super().__init__()
		self.name = name
		self.extension = extension
		self.extension_options = extension_options
		self.answer_count = answer_count
		self.limit_time = limit_time
		self.user_uid = user_uid
