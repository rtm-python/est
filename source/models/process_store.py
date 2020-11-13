# -*- coding: utf-8 -*-

'''
Store module for Process entity.
'''

# Application modules import
from models import database
from models.__base__ import Store
from models.entity.process import Process
from models.entity.examination import Examination


class ProcessStore(Store):
	"""
	This is a process store class.
	"""

	@staticmethod
	def create(examination_id: int,
						 plugin: str, plugin_options: str,
						 name: str, repeat: int, performance: int
						 ) -> Process:
		"""
		Create and return process.
		"""
		return super(ProcessStore, ProcessStore).create(
			Process(
				examination_id,
				plugin, plugin_options,
				name, repeat, performance
			)
		)

	@staticmethod
	def read(uid: str) -> Process:
		"""
		Return process by uid (only not deleted).
		"""
		return super(ProcessStore, ProcessStore).read(
			Process, uid
		)

	@staticmethod
	def update(uid: str, examination_id: int,
						 plugin: str, plugin_options: str,
						 name: str, repeat: int, performance: int
						 ) -> Process:
		"""
		Update and return process.
		"""
		process = ProcessStore.read(uid)
		process.examination_id = examination_id
		process.plugin = plugin
		process.plugin_options = plugin_options
		process.name = name
		process.repeat = repeat
		process.performance = performance
		return super(ProcessStore, ProcessStore).update(
			process
		)

	@staticmethod
	def delete(uid: str) -> Process:
		"""
		Delete and return process.
		"""
		return super(ProcessStore, ProcessStore).delete(
			ProcessStore.read(uid)
		)

	@staticmethod
	def read_list(offset: int, limit: int,
								filter_examination_id: int
								) -> list:
		"""
		Return list of processes by arguments.
		"""
		return _get_list_query(
			filter_examination_id
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(filter_examination_id: int) -> int:
		"""
		Return number of processes in list.
		"""
		return Store.count(_get_list_query(
			filter_examination_id
		))

	@staticmethod
	def add_answer(uid: str, is_correct: bool) -> Process:
		"""
		Increment and return answer count and
		if answer is correct then insrement correct count.
		"""
		process = ProcessStore.read(uid)
		process.answer_count += 1
		if is_correct:
			process.correct_count += 1
		return super(ProcessStore, ProcessStore).update(
			process
		)

	@staticmethod
	def get(id: int) -> Process:
		"""
		Return process bt id (no matter deleted or etc.).
		"""
		return super(ProcessStore, ProcessStore).get(
			Process, id
		)

def _get_list_query(filter_examination_id: int):
	"""
	Return query object for process.
	"""
	return database.session.query(
		Process
	).join(
		Examination
	).filter(
		True if filter_examination_id is None else \
			filter_examination_id == Examination.id,
		Examination.deleted_utc == None,
		Process.deleted_utc == None
	).order_by(
		Process.modified_utc.desc()
	)
