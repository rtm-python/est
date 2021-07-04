# -*- coding: utf-8 -*-

'''
Store module for Name entity.
'''

# Application modules import
from models import database
from models.__base__ import Store
from models.entity.name import Name


class NameStore(Store):
	"""
	This is a name store class.
	"""

	@staticmethod
	def create(user_id: int, value: str) -> Name:
		"""
		Create and return name.
		"""
		return super(NameStore, NameStore).create(
			Name(user_id, value)
		)

	@staticmethod
	def read(uid: str) -> Name:
		"""
		Return name by uid (only not deleted).
		"""
		return super(NameStore, NameStore).read(
			Name, uid
		)

	@staticmethod
	def update(uid: str, user_id: int, value: str) -> Name:
		"""
		Update and return name.
		"""
		name = NameStore.read(uid)
		name.user_id = user_id
		name.value = value
		return super(NameStore, NameStore).update(
			name
		)

	@staticmethod
	def delete(uid: str) -> Name:
		"""
		Delete and return name.
		"""
		return super(NameStore, NameStore).delete(
			NameStore.read(uid)
		)

	@staticmethod
	def read_list(offset: int, limit: int,
							  filter_user_id: int, filter_value: str) -> list:
		"""
		Return list of names by arguments.
		"""
		return _get_list_query(
			filter_user_id, filter_value
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(filter_user_id: int, filter_value: str) -> int:
		"""
		Return number of names in list.
		"""
		return Store.count(_get_list_query(
			filter_user_id, filter_value
		))

	@staticmethod
	def set_value(uid: str, value: str) -> Name:
		"""
		Set name value and return name.
		"""
		name = NameStore.read(uid)
		name.value = value
		return super(NameStore, NameStore).update(
			name
		)

	@staticmethod
	def get(id: int) -> Name:
		"""
		Return name by id (no matter deleted or etc.).
		"""
		return super(NameStore, NameStore).get(
			Name, id
		)


def _get_list_query(filter_user_id: int, filter_value: str):
	"""
	Return query object for name based on arguments.
	"""
	return database.session.query(
		Name
	).filter(
		True if filter_user_id is None else \
			Name.user_id == filter_user_id,
		True if filter_value is None else \
			Name.value.contains(filter_value),
		Name.deleted_utc == None
	).order_by(
		Name.modified_utc.desc()
	)
