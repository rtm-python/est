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
	test_id = Column(
		database.Integer, ForeignKey('test.id'),
		index=True, nullable=False
	)
	answer_count = Column(
		database.Integer, default=0,
		index=True, nullable=False
	)
	correct_count = Column(
		database.Integer, default=0,
		index=True, nullable=False
	)
	limit_time = Column(
		database.Integer, default=0,
		index=True, nullable=False
	)
	answer_time = Column(
		database.Integer, default=0,
		index=True, nullable=False
	)
	user_uid = Column(database.String, index=True, nullable=True)
	anonymous_token = Column(database.String, index=True, nullable=True)
	name_uid = Column(database.String, index=True, nullable=True)

	def __init__(self, test_id: int,
							 user_uid: str, anonymous_token: str,
							 name_uid: str) -> "Process":
		'''
		Initiate object and stores Process' data.
		'''
		super().__init__()
		self.test_id = test_id
		self.user_uid = user_uid
		self.anonymous_token = anonymous_token
		self.name_uid = name_uid
