# -*- coding: utf-8 -*-

'''
Store module for Process entity.
'''

# Standard libraries import
import json

# Application modules import
from models import database
from models.__base__ import Store
from models.entity.task import Task
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
						 name: str, repeat: int, performance: int,
						 answer_count: int, correct_count: int,
						 total_answer_time: int, performance_time: int,
						 result: int
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
		process.answer_count = answer_count
		process.correct_count = correct_count
		process.total_answer_time = total_answer_time
		process.performance_time = performance_time
		process.result = result
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
	def add_answer(uid: str, task: Task) -> Process:
		"""
		Return process after increment answer count and
		if answer is correct then insrement correct count.
		Also calculate answer and performance time.
		"""
		process = ProcessStore.read(uid)
		process.answer_count += 1
		data = json.loads(task.data)
		if task.answer == data['answer']:
			process.correct_count += 1
		process.total_answer_time += \
			(task.modified_utc - task.created_utc).total_seconds()
		process.performance_time += \
			int(data['performance_time'] / process.performance * 100)
		if process.answer_count >= process.repeat:
			correctness = int(process.correct_count / process.answer_count * 100)
			performance = \
				int(process.performance_time / process.total_answer_time * 100)
			if performance > 100:
				performance = 100
			process.result = int(correctness * performance / 100)
		return super(ProcessStore, ProcessStore).update(
			process
		)

	@staticmethod
	def calculate_result(uid: str, result: int) -> Process:
		"""
		Set result and return process.
		"""
		process = ProcessStore.read(uid)
		process.result = result
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
