# -*- coding: utf-8 -*-

'''
Entity module for user entity.
'''

# Additional libraries import
from sqlalchemy import Column

# Project modules imports
from models import database
from models.entity.__base__ import Entity


class User(Entity):
	'''
	This is a class for User entity.
	'''
	__tablename__ = 'user'
	from_id = Column(database.String, index=True, nullable=False)
	name = Column(database.String, index=True, nullable=True)
	notification_profile = Column(database.Boolean, index=True, nullable=True)
	notification_test_start = Column(database.Boolean, index=True, nullable=True)
	notification_test_complete = Column(database.Boolean, index=True, nullable=True)

	def __init__(self, from_id: str, name: str) -> "User":
		'''
		Initiate object and stores User's data.
		'''
		super().__init__()
		self.from_id = from_id
		self.name = name
