# -*- coding: utf-8 -*-

'''
Store module for Process entity.
'''

# Standard libraries import
import datetime
import math

# Additional libraries import
from sqlalchemy import Column, ForeignKey, Enum as SAEnum, func, or_

# Application modules import
from models import database
from models import count
from models.entity.process import Process
from models.entity.examination import Examination


def create_process(examination_id: int,
									 plugin: str, plugin_options: str,
									 name: str, repeat: int, performance: int
									 ) -> Process:
	"""
	Create process and return created entity.
	"""
	process = Process(examination_id,
    								plugin, plugin_options,
										name, repeat, performance)
	database.session.add(process)
	database.session.commit()
	return process


def read_process(uid: str) -> Process:
	"""
	Return process entity by uid.
	"""
	return Process.query.filter_by(uid=uid).first()


def update_process(uid: str, examination_id: int,
									 plugin: str, plugin_options: str,
									 name: str, repeat: int, performance: int
									 ) -> Examination:
	'''
	Update process and return updated entity.
	'''
	process = read_process(uid)
	process.examination_id = examination_id
	process.plugin = plugin
	process.plugin_options = plugin_options
	process.name = name
	process.repeat = repeat
	process.performance = performance
	process.set_modified()
	database.session.commit()


def delete_process(uid: str) -> Process:
	'''
	Delete process by set_deleted and return deleted entity.
	'''
	process = read_process(uid)
	process.set_deleted()
	database.session.commit()


def _get_list_query(filter_examination_id: int):
	"""
	Return query object for process based on arguments.
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


def read_process_list(offset: int, limit: int,
											filter_examination_id: int
											) -> [tuple]:
	"""
	Return filtered list of dictionaries filled with entity fields.
	"""
	return _get_list_query(
		filter_examination_id
	).limit(limit).offset(offset).all()


def count_process_list(filter_examination_id: int) -> int:
	"""
	Return items number in filtered list of entities.
	"""
	return count(_get_list_query(filter_examination_id))


def update_answered(uid: str, is_correct: bool) -> None:
	"""
	Increment answered and correct.
	"""
	process = read_process(uid)
	process.answered_count += 1
	if is_correct:
		process.correct_count += 1
	process.set_modified()
	database.session.commit()
