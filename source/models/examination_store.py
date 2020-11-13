# -*- coding: utf-8 -*-

'''
Store module for Examination entity.
'''

# Application modules import
from models import database
from models.__base__ import Store
from models.entity.examination import Examination


class ExaminationStore(Store):
	"""
	This is an examination store class.
	"""

	@staticmethod
	def create(name: str, description: str,
						 plugin: str, plugin_options: str,
						 default_repeat: int, default_performance: int
						 ) -> Examination:
		"""
		Create and return examination.
		"""
		return super(ExaminationStore, ExaminationStore).create(
			Examination(
				name, description,
				plugin, plugin_options,
				default_repeat, default_performance
			)
		)

	@staticmethod
	def read(uid: str) -> Examination:
		"""
		Return examination by uid (only not deleted).
		"""
		return super(ExaminationStore, ExaminationStore).read(
			Examination, uid
		)

	@staticmethod
	def update(uid: str, name: str, description: str,
						 plugin: str, plugin_options: str,
						 default_repeat: int, default_performance: int
						 ) -> Examination:
		"""
		Update and return examination.
		"""
		examination = ExaminationStore.read(uid)
		examination.name = name
		examination.description = description
		examination.plugin = plugin
		examination.plugin_options = plugin_options
		examination.default_repeat = default_repeat
		examination.default_performance = default_performance
		return super(ExaminationStore, ExaminationStore).update(
			examination
		)

	@staticmethod
	def delete(uid: str) -> Examination:
		"""
		Delete and return examination.
		"""
		return super(ExaminationStore, ExaminationStore).delete(
			ExaminationStore.read(uid)
		)

	@staticmethod
	def read_list(offset: int, limit: int,
								filter_name: str, filter_plugin: str,
								filter_hide_global: bool
								) -> list:
		"""
		Return list of examinations by arguments.
		"""
		return _get_list_query(
			filter_name, filter_plugin, filter_hide_global
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(filter_name: str, filter_plugin: str,
								 filter_hide_global: bool
								 ) -> int:
		"""
		Return number of examinations in list
		"""
		return Store.count(_get_list_query(
			filter_name, filter_plugin, filter_hide_global
		))

	@staticmethod
	def get(id: int) -> Examination:
		"""
		Return examination by id (no matter deleted or etc.)
		"""
		return super(ExaminationStore, ExaminationStore).get(
			Examination, id
		)


def _get_list_query(filter_name: str, filter_plugin: str,
										filter_hide_global: bool
										):
	"""
	Return query object for examination.
	"""
	return database.session.query(
		Examination
	).filter(
		True if filter_name is None else \
			Examination.name.contains(filter_name),
		True if filter_plugin is None else \
			Examination.plugin.contains(filter_plugin),
		Examination.deleted_utc == None
	).order_by(
		Examination.modified_utc.desc()
	)
