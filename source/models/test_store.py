# -*- coding: utf-8 -*-

'''
Store module for Test entity.
'''

# Application modules import
from models import database
from models.__base__ import Store
from models.entity.test import Test


class TestStore(Store):
	"""
	This is an test store class.
	"""

	@staticmethod
	def create(name: str, plugin: str, plugin_options: str,
						 repeat: int, speed: int, user_uid: str) -> Test:
		"""
		Create and return test.
		"""
		return super(TestStore, TestStore).create(
			Test(
				name, plugin, plugin_options, repeat, speed, user_uid
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
	def update(uid: str, name: str, plugin_options: str,
						 repeat: int, speed: int) -> Test:
		"""
		Update and return test.
		"""
		test = TestStore.read(uid)
		test.name = name
		test.plugin_options = plugin_options
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
								filter_name: str, filter_plugin: str,
								filter_user_uid: str) -> list:
		"""
		Return list of tests by arguments.
		"""
		return _get_list_query(
			filter_name, filter_plugin, filter_user_uid
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(filter_name: str, filter_plugin: str,
								 filter_user_uid: str) -> int:
		"""
		Return number of tests in list
		"""
		return Store.count(_get_list_query(
			filter_name, filter_plugin, filter_user_uid
		))

	@staticmethod
	def get(id: int) -> Test:
		"""
		Return test by id (no matter deleted or etc.)
		"""
		return super(TestStore, TestStore).get(
			Test, id
		)


def _get_list_query(filter_name: str, filter_plugin: str,
										filter_user_uid: str):
	"""
	Return query object for test.
	"""
	return database.session.query(
		Test
	).filter(
		True if filter_name is None else \
			Test.name.contains(filter_name),
		True if filter_plugin is None else \
			Test.plugin.contains(filter_plugin),
		True if filter_user_uid is None else \
			Test.user_uid == filter_user_uid,
		Test.deleted_utc == None
	).order_by(
		Test.modified_utc.desc()
	)
