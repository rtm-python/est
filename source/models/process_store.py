# -*- coding: utf-8 -*-

'''
Store module for Process entity.
'''

# Standard libraries import
import json

# Application modules import
from models import database
from models.__base__ import Store
from models.entity.process import Process
from models.entity.test import Test
from models.entity.task import Task


class ProcessStore(Store):
	"""
	This is a process store class.
	"""

	@staticmethod
	def create(test_id: int, user_uid: str, anonymous_token: str) -> Process:
		"""
		Create and return process.
		"""
		return super(ProcessStore, ProcessStore).create(
			Process(
				test_id, user_uid, anonymous_token
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
	def update(uid: str, test_id: int,
						 user_uid: str, anonymous_token: str,
						 answer_count: int, correct_count: int,
						 total_answer_time: int, speed_time: int,
						 result: int) -> Process:
		"""
		Update and return process.
		"""
		process = ProcessStore.read(uid)
		process.test_id = test_id
		process.user_uid = user_uid
		process.anonymous_token = anonymous_token
		process.answer_count = answer_count
		process.correct_count = correct_count
		process.total_answer_time = total_answer_time
		process.speed_time = speed_time
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
								filter_name: str, filter_plugin: str,
								filter_hide_completed: bool,
								user_uid: str, anonymous_token: str) -> list:
		"""
		Return list of processes by arguments.
		"""
		return _get_list_query(
			filter_name, filter_plugin, filter_hide_completed,
			user_uid, anonymous_token
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(filter_name: str, filter_plugin: str,
								 filter_hide_completed: bool,
								 user_uid: str, anonymous_token: str) -> int:
		"""
		Return number of processes in list.
		"""
		return Store.count(_get_list_query(
			filter_name, filter_plugin, filter_hide_completed,
			user_uid, anonymous_token
		))

	@staticmethod
	def add_answer(uid: str, task: Task) -> Process:
		"""
		Return process after increment answer count and
		if answer is correct then insrement correct count.
		Also calculate answer and speed time.
		"""
		process, test = ProcessStore.read_with_test(uid)
		process.answer_count += 1
		data = json.loads(task.data)
		if task.correct_answer:
			process.correct_count += 1
		process.total_answer_time += \
			int((task.modified_utc - task.created_utc).total_seconds())
		process.speed_time += \
			int(data['speed_time'] / test.speed * 100)
		if process.answer_count >= test.repeat:
			correctness = int(process.correct_count / process.answer_count * 100)
			speed = \
				int(process.speed_time / process.total_answer_time * 100)
			if speed > 100:
				speed = 100
			process.result = int(correctness * speed / 100)
		return super(ProcessStore, ProcessStore).update(
			process
		)

	@staticmethod
	def set_result(uid: str, result: int) -> Process:
		"""
		Set result and return process.
		"""
		process = ProcessStore.read(uid)
		process.result = result
		return super(ProcessStore, ProcessStore).update(
			process
		)

	@staticmethod
	def bind_token(user_uid: str, anonymous_token: str) -> int:
		"""
		Bind (replace anonymous_token with user_uid) processes
		and return binded process number.
		"""
		binded_count = 0
		while True:
			process_list = ProcessStore.read_list(
				0, 100, None, None, None, None, anonymous_token)
			if len(process_list) == 0:
				break
			else:
				for process, test in process_list:
					process.user_uid = user_uid
					process.anonymous_token = None
					super(ProcessStore, ProcessStore).update(process)
					binded_count += 1
		return binded_count

	@staticmethod
	def get(id: int) -> Process:
		"""
		Return process bt id (no matter deleted or etc.).
		"""
		return super(ProcessStore, ProcessStore).get(
			Process, id
		)

	@staticmethod
	def read_with_test(uid: str):
		"""
		Return process with test data.
		"""
		return database.session.query(
			Process, Test
		).join(
			Test
		).filter(
 			uid == Process.uid
		).first()


def _get_list_query(filter_name: str, filter_plugin: str,
										filter_hide_completed: bool,
										user_uid: str, anonymous_token: str):
	"""
	Return query object for process.
	"""
	return database.session.query(
		Process, Test
	).join(
		Test
	).filter(
		True if filter_name is None else \
			filter_name == Test.name,
		True if filter_plugin is None else \
			filter_plugin == Test.plugin,
		True if filter_hide_completed is None or \
			filter_hide_completed is False else \
			Process.result == None,
		True if user_uid is None else \
			user_uid == Process.user_uid,
		True if anonymous_token is None else \
			anonymous_token == Process.anonymous_token,
		Process.deleted_utc == None
	).order_by(
		Process.modified_utc.desc()
	)
