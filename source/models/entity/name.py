# -*- coding: utf-8 -*-

'''
Entity module for name entity.
'''

# Additional libraries import
from sqlalchemy import Column
from sqlalchemy import ForeignKey

# Project modules imports
from models import database
from models.entity.__base__ import Entity


class Name(Entity):
	'''
	This is a class for Name entity.
	'''
	__tablename__ = 'name'
	user_id = Column(
		database.Integer, ForeignKey('user.id'),
		index=True, nullable=True
	)
	value = Column(database.String, index=True, nullable=False)

	def __init__(self, user_id: int, value: str) -> "Name":
		'''
		Initiate object and stores Name's data.
		'''
		super().__init__()
		self.user_id = user_id
		self.value = value
