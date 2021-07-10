# -*- coding: utf-8 -*-

'''
Base module for base store.
'''

# Additional libraries import
from sqlalchemy import func

# Application modules import
from models import database
from models.entity.__base__ import Entity


class Store():
	"""
	"""
	__abstract__ = True

	@staticmethod
	def create(entity: Entity) -> Entity:
		"""
		Create and return entity.
		"""
		try:
			database.session.add(entity)
			database.session.commit()
			return entity
		except:
			database.session.rollback()
			raise

	@staticmethod
	def read(entity_class, uid: str) -> Entity:
		"""
		Return entity by uid (only not deleted).
		"""
		return entity_class.query.filter_by(
			uid=uid, deleted_utc=None).first()

	@staticmethod
	def update(entity: Entity) -> Entity:
		"""
		Update and return entity.
		"""
		try:
			entity.set_modified()
			database.session.commit()
			return entity
		except:
			database.session.rollback()
			raise


	@staticmethod
	def delete(entity: Entity) -> Entity:
		"""
		Delete and return entity.
		"""
		try:
			entity.set_deleted()
			database.session.commit()
			return entity
		except:
			database.session.rollback()
			raise

	@staticmethod
	def get(entity_class, id: int) -> Entity:
		"""
		Return entity by id (no matter deleted or etc.).
		"""
		return entity_class.query.get(id)

	@staticmethod
	def count(query) -> int:
		"""
		Return number of elements (rows) in resulted query.
		"""
		return database.session.execute(
			query.statement.with_only_columns([func.count()]).order_by(None)
		).scalar() or 0
