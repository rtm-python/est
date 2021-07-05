# -*- coding: utf-8 -*-

'''
Store module for Test entity.
'''

# Application modules import
from models import database
from models.__base__ import Store
from models.entity.test import Test

# Additional libraries import
from sqlalchemy import or_

class TestStore(Store):
	"""
	This is an test store class.
	"""

	@staticmethod
	def create(name: str, extension: str, extension_options: str,
						 repeat: int, speed: int, user_uid: str) -> Test:
		"""
		Create and return test.
		"""
		return super(TestStore, TestStore).create(
			Test(
				name, extension, extension_options, repeat, speed, user_uid
			)
		)

	@staticmethod
	def read(uid: str) -> Test:
		"""
		Return test by uid (only not deleted).
		"""
		return super(TestStore, TestStore).read(
			Test, uid
		)

	@staticmethod
	def update(uid: str, name: str, extension_options: str,
						 repeat: int, speed: int) -> Test:
		"""
		Update and return test.
		"""
		test = TestStore.read(uid)
		test.name = name
		test.extension_options = extension_options
		test.repeat = repeat
		test.speed = speed
		return super(TestStore, TestStore).update(
			test
		)

	@staticmethod
	def delete(uid: str) -> Test:
		"""
		Delete and return test.
		"""
		return super(TestStore, TestStore).delete(
			TestStore.read(uid)
		)

	@staticmethod
	def read_list(offset: int, limit: int,
								filter_name: str, filter_extension: str,
								filter_user_uid: str,
								filter_admin_user_uid_list: list) -> list:
		"""
		Return list of tests by arguments.
		"""
		return _get_list_query(
			filter_name, filter_extension, filter_user_uid,
			filter_admin_user_uid_list
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(filter_name: str, filter_extension: str,
								 filter_user_uid: str,
								 filter_admin_user_uid_list: list) -> int:
		"""
		Return number of tests in list
		"""
		return Store.count(_get_list_query(
			filter_name, filter_extension, filter_user_uid,
			filter_admin_user_uid_list
		))

	@staticmethod
	def get(id: int) -> Test:
		"""
		Return test by id (no matter deleted or etc.)
		"""
		return super(TestStore, TestStore).get(
			Test, id
		)


def _get_list_query(filter_name: str, filter_extension: str,
										filter_user_uid: str, filter_admin_user_uid_list: list):
	"""
	Return query object for test.
	"""
	if filter_user_uid in filter_admin_user_uid_list:
		user_uid_expression = True
	else:
		user_uid_expression = or_(
			Test.user_uid == user_uid \
				for user_uid in [ filter_user_uid ] + filter_admin_user_uid_list
		)
	return database.session.query(
		Test
	).filter(
		True if filter_name is None else \
			Test.name.ilike('%' + filter_name + '%'),
		True if filter_extension is None else \
			Test.extension.ilike('%' + filter_extension + '%'),
		user_uid_expression,
		Test.deleted_utc == None
	).order_by(
		Test.modified_utc.desc()
	)
