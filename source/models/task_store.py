# -*- coding: utf-8 -*-

'''
Store module for Task entity.
'''

# Standard libraries import
import datetime
import math

# Additional libraries import
from sqlalchemy import Column, ForeignKey, Enum as SAEnum, func, or_

# Application modules import
from models import database
from models import count
from models.entity.task import Task
from models.entity.process import Process


def create_task(process_id: int, data: str) -> Task:
	"""
	Create task and return created entity.
	"""
	task = Task(process_id, data)
	database.session.add(task)
	database.session.commit()
	return task


def read_task(uid: str) -> Task:
	"""
	Return task entity by uid.
	"""
	return Task.query.filter_by(uid=uid).first()


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


def read_task_list(offset: int, limit: int,
									 filter_process_id: int
									 ) -> [tuple]:
	"""
	Return filtered list of dictionaries filled with entity fields.
	"""
	return _get_list_query(
		filter_process_id
	).limit(limit).offset(offset).all()


def count_task_list(filter_process_id: int) -> int:
	"""
	Return items number in filtered list of entities.
	"""
	return count(_get_list_query(filter_process_id))


def set_answer(uid: str, answer: str) -> None:
	"""
	Set answer.
	"""
	task = read_task(uid)
	task.answer = answer
	task.set_modified()
	database.session.commit()
