# -*- coding: utf-8 -*-

'''
Store module for Task entity.
'''

# Application modules import
from models import database
from models.__base__ import Store
from models.entity.task import Task
from models.entity.process import Process


class TaskStore(Store):
	"""
	This is a task class.
	"""

	@staticmethod
	def create(process_id: int, data: str) -> Task:
		"""
		Create and return task.
		"""
		return super(TaskStore, TaskStore).create(
			Task(process_id, data)
		)

	@staticmethod
	def read(uid: str) -> Task:
		"""
		Return task by uid (only not deleted).
		"""
		return super(TaskStore, TaskStore).read(
			Task, uid
		)

	@staticmethod
	def update(uid: str, process_id: int, data: str, answer: str) -> Task:
		"""
		Update and return task.
		"""
		task = TaskStore.read(uid)
		task.process_id = process_id
		task.data = data
		task.answer = answer
		return super(TaskStore, TaskStore).update(
			task
		)

	@staticmethod
	def delete(uid: str) -> Task:
		"""
		Delete and return task.
		"""
		return super(TaskStore, TaskStore).delete(
			TaskStore.read(uid)
		)

	@staticmethod
	def read_list(offset: int, limit: int,
							  filter_process_id: int
								) -> list:
		"""
		Return list of tasks by arguments.
		"""
		return _get_list_query(
			filter_process_id
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(filter_process_id: int) -> int:
		"""
		Return number of tasks in list.
		"""
		return Store.count(_get_list_query(
			filter_process_id
		))

	@staticmethod
	def set_answer(uid: str, answer: str) -> Task:
		"""
		Set user answer and return task.
		"""
		task = TaskStore.read(uid)
		task.answer = answer
		return super(TaskStore, TaskStore).update(
			task
		)

	@staticmethod
	def get(id: int) -> Task:
		"""
		Return task by id (no matter deleted or etc.).
		"""
		return super(TaskStore, TaskStore).get(
			Task, id
		)


def _get_list_query(filter_process_id: int):
	"""
	Return query object for task based on arguments.
	"""
	return database.session.query(
		Task
	).join(
		Process
	).filter(
		True if filter_process_id is None else \
			filter_process_id == Process.id,
		Task.answer == None,
		Process.deleted_utc == None,
		Task.deleted_utc == None
	).order_by(
		Task.modified_utc.desc()
	)
