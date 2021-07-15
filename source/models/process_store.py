# -*- coding: utf-8 -*-

'''
Store module for Process entity.
'''

# Standard libraries import
import json
import datetime

# Application modules import
from models import database
from models.__base__ import Store
from models.entity.process import Process
from models.entity.test import Test
from models.entity.task import Task
from models.entity.name import Name

# Additional libraries import
import sqlalchemy
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import and_
from sqlalchemy import desc
from sqlalchemy.sql.expression import literal
from sqlalchemy.sql.expression import cast


class ProcessStore(Store):
	"""
	This is a process store class.
	"""

	@staticmethod
	def create(test_id: int, user_uid: str, anonymous_token: str,
						 name_uid: str) -> Process:
		"""
		Create and return process.
		"""
		return super(ProcessStore, ProcessStore).create(
			Process(
				test_id, user_uid, anonymous_token, name_uid
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
						 user_uid: str, anonymous_token: str, name_uid: str,
						 answer_count: int, correct_count: int,
						 limit_time: int, answer_time: int) -> Process:
		"""
		Update and return process.
		"""
		process = ProcessStore.read(uid)
		process.test_id = test_id
		process.user_uid = user_uid
		process.anonymous_token = anonymous_token
		process.name_uid = name_uid
		process.answer_count = answer_count
		process.correct_count = correct_count
		process.limit_time = limit_time
		process.answer_time = answer_time
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
								filter_name: str, filter_extension: str,
								filter_hide_completed: bool,
								filter_user_uid: str, filter_anonymous_token: str,
								filter_name_uid: str,
								result_expression = literal(0),
								crammers_expression = literal(0)) -> list:
		"""
		Return list of processes by arguments.
		"""
		return _get_list_query(
			filter_name, filter_extension, filter_hide_completed,
			filter_user_uid, filter_anonymous_token, filter_name_uid,
			result_expression, crammers_expression
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_list(filter_name: str, filter_extension: str,
								 filter_hide_completed: bool,
								 filter_user_uid: str, filter_anonymous_token: str,
								 filter_name_uid: str,
								 result_expression = literal(0),
								 crammers_expression = literal(0)) -> int:
		"""
		Return number of processes in list.
		"""
		return Store.count(_get_list_query(
			filter_name, filter_extension, filter_hide_completed,
			filter_user_uid, filter_anonymous_token, filter_name_uid,
			result_expression, crammers_expression
		))

	@staticmethod
	def add_answer(uid: str, task: Task) -> Process:
		"""
		Return process after increment answer count and
		if answer is correct then insrement correct count.
		Also calculate answer and limit time.
		"""
		process, test, _, _ = ProcessStore.read_with_test(uid)
		process.answer_count += 1
		data = json.loads(task.data)
		if task.correct_answer:
			process.correct_count += 1
		process.answer_time += \
			int((task.modified_utc - task.created_utc).total_seconds())
		process.limit_time += int(data['limit_time'])
		if process.answer_count >= test.answer_count:
			correctness = int(process.correct_count / process.answer_count * 100)
			speed = \
				int(process.answer_time / process.limit_time * 100)
			if speed > 100:
				speed = 100
			# process.result = int(correctness * speed / 100)
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
				0, 100, None, None, None, None, anonymous_token, None)
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
	def read_with_test(uid: str,
										 result_expression = literal(0),
										 crammers_expression = literal(0)):
		"""
		Return process with test data.
		"""
		return database.session.query(
			Process, Test,
			cast(result_expression, sqlalchemy.Integer),
			cast(crammers_expression, sqlalchemy.Integer)
		).join(
			Test
		).filter(
 			uid == Process.uid
		).first()

	@staticmethod
	def read_charts(offset: int, limit: int,
								  filter_name: str, filter_extension: str,
								  user_uid: str, anonymous_token: str,
									name_uid) -> list:
		"""
		Return list of process charts by arguments.
		"""
		return _get_charts_query(
			filter_name, filter_extension,
			user_uid, anonymous_token, name_uid, False
		).limit(limit).offset(offset).all()

	@staticmethod
	def count_charts(filter_name: str, filter_extension: str,
								   user_uid: str, anonymous_token: str,
									 name_uid: str) -> int:
		"""
		Return number of process charts in list.
		"""
		return _get_charts_query(
			filter_name, filter_extension,
			user_uid, anonymous_token, name_uid, True
		)
		# TODO: Issue with simplified query
		return Store.count(_get_charts_query(
			filter_name, filter_extension,
			user_uid, anonymous_token, name_uid, True
		))

	@staticmethod
	def get_top_crammers(offset: int, limit: int,
											 filter_extension: str,
											 filter_user_uid: str,
											 filter_anonymous_token: str,
											 filter_name_uid: str,
											 crammers_expression,
											 since: datetime.datetime,
											 until: datetime.datetime,
											 tz_delta: datetime.timedelta) -> list:
		pre = _get_crammers_subquery(
			filter_extension, filter_user_uid, filter_anonymous_token,
			filter_name_uid, crammers_expression, since, until, tz_delta
		)
		return database.session.query(
			pre.c.name_value.label('name'),
			func.count(pre.c.process_id).label('process_count'),
			func.sum(pre.c.process_correct_count).label('correct_count'),
			func.sum(pre.c.process_answer_time).label('answer_time'),
			func.sum(pre.c.crammers).label('total'),
		).group_by(
			pre.c.name_id
		).order_by(
			desc('total'),
			pre.c.process_modified_utc
		).limit(limit).offset(offset).all()

	@staticmethod
	def get_chart_data(filter_extension: str,
										 filter_user_uid: str,
										 filter_anonymous_token: str,
										 filter_name_uid: str,
										 crammers_expression,
										 since: datetime.datetime,
										 until: datetime.datetime,
										 tz_delta: datetime.timedelta) -> list:
		pre = _get_crammers_subquery(
			filter_extension, filter_user_uid, filter_anonymous_token,
			filter_name_uid, crammers_expression, since, until, tz_delta
		)
		pre_local = database.session.query(
			pre.c.process_correct_count,
			pre.c.process_answer_time,
			pre.c.process_id,
			# pre.c.test_extension,
			pre.c.test_id,
			pre.c.name_value,
			pre.c.name_id,
			pre.c.crammers,
			pre.c.process_modified_utc.label('process_modified_local'),
			func.strftime(
				'%Y-%m-%d', pre.c.process_modified_utc
			).label('process_date_local')
		).subquery()
		return database.session.query(
			pre_local.c.name_value.label('name_value'),
			# pre_local.c.test_extension,
			func.count(pre_local.c.process_id).label('process_count'),
			func.sum(pre_local.c.process_correct_count).label('correct_count'),
			func.sum(pre_local.c.process_answer_time).label('answer_time'),
			func.sum(pre_local.c.crammers).label('total'),
			pre_local.c.process_date_local
		).group_by(
			pre_local.c.name_value,
			# pre_local.c.test_extension,
			pre_local.c.process_date_local
		).order_by(
			pre_local.c.process_modified_local
		).all()


def _get_list_query(filter_name: str, filter_extension: str,
										filter_hide_completed: bool,
										filter_user_uid: str, filter_anonymous_token: str,
										filter_name_uid: str,
										result_expression, crammers_expression):
	"""
	Return query object for process.
	"""
	if filter_name_uid is None:
		pre = database.session.query(
			Process, Test, Name,
			cast(result_expression, sqlalchemy.Integer),
			cast(crammers_expression, sqlalchemy.Integer)
		).join(
			Test
		).outerjoin(
			Name, Name.uid == Process.name_uid
		)
	else:
		pre = database.session.query(
			Process, Test, Name,
			cast(result_expression, sqlalchemy.Integer),
			cast(crammers_expression, sqlalchemy.Integer)
		).join(
			Test
		).join(
			Name, Name.uid == filter_name_uid
		)
	return pre.filter(
		True if filter_name is None else \
			Test.name.ilike('%' + filter_name + '%'),
		True if filter_extension is None else \
			Test.extension.ilike('%' + filter_extension + '%'),
		True if filter_hide_completed is None or \
			filter_hide_completed is False else \
				Process.answer_count < Test.answer_count,
		True if filter_user_uid is None else \
			filter_user_uid == Process.user_uid,
		True if filter_anonymous_token is None else \
			filter_anonymous_token == Process.anonymous_token,
		True if filter_name_uid is None else \
			filter_name_uid == Process.name_uid,
		Process.deleted_utc == None
	).order_by(
		Process.modified_utc.desc()
	)


def _get_charts_query(filter_name: str, filter_extension: str,
										  filter_user_uid: str, filter_anonymous_token: str,
											filter_name_uid: str, is_count_query: bool):
	"""
	Return query object for process charts.
	"""
	pre = database.session.query(
		Test.id.label('test_id'), Test.name.label('name'),
		Process.modified_utc.label('modified_utc'),
		func.strftime('%w', Process.modified_utc).label('weekday'),
		Process.result.label('result')
	).join(
		Process
	).filter(
		True if filter_name is None else \
			Test.name.ilike('%' + filter_name + '%'),
		True if filter_extension is None else \
			Test.extension.ilike('%' + filter_extension + '%'),
		True if filter_user_uid is None else \
			filter_user_uid == Process.user_uid,
		True if filter_anonymous_token is None else \
			filter_anonymous_token == Process.anonymous_token,
		True if filter_name_uid is None else \
			filter_name_uid == Process.name_uid,
		Process.modified_utc >= \
				datetime.datetime.utcnow() - datetime.timedelta(days=7),
		Test.deleted_utc == None
	).subquery()
	if is_count_query: # Return simplified query for count
		return len(
			database.session.query(
				Test.id
			).join(
				pre, pre.c.test_id == Test.id
			).group_by(
				Test.id
			).all()
		)
	# Prepare queries for each weekday
	weekday = int(datetime.datetime.utcnow().strftime('%w'))
	weekdays = []
	for index in range(7):
		weekday = weekday + 1 if weekday < 6 else 0
		weekdays += [
			database.session.query(
				pre.c.test_id, pre.c.modified_utc, pre.c.weekday,
				func.count(pre.c.result).label('count'),
				func.avg(pre.c.result).label('result')
			).filter(
				pre.c.weekday == str(weekday),
				pre.c.result != None
			).group_by(
				pre.c.test_id
			).order_by(
				pre.c.modified_utc.desc()
			).subquery()
		]
	return database.session.query(
		Test.uid, Test.name, Test.extension,
		weekdays[0].c.weekday, weekdays[0].c.count, weekdays[0].c.result,
		weekdays[1].c.weekday, weekdays[1].c.count, weekdays[1].c.result,
		weekdays[2].c.weekday, weekdays[2].c.count, weekdays[2].c.result,
		weekdays[3].c.weekday, weekdays[3].c.count, weekdays[3].c.result,
		weekdays[4].c.weekday, weekdays[4].c.count, weekdays[4].c.result,
		weekdays[5].c.weekday, weekdays[5].c.count, weekdays[5].c.result,
		weekdays[6].c.weekday, weekdays[6].c.count, weekdays[6].c.result
	).outerjoin(
		weekdays[0], Test.id == weekdays[0].c.test_id
	).outerjoin(
		weekdays[1], Test.id == weekdays[1].c.test_id
	).outerjoin(
		weekdays[2], Test.id == weekdays[2].c.test_id
	).outerjoin(
		weekdays[3], Test.id == weekdays[3].c.test_id
	).outerjoin(
		weekdays[4], Test.id == weekdays[4].c.test_id
	).outerjoin(
		weekdays[5], Test.id == weekdays[5].c.test_id
	).outerjoin(
		weekdays[6], Test.id == weekdays[6].c.test_id
	).filter(
		or_(
			weekdays[0].c.result != None,
			weekdays[1].c.result != None,
			weekdays[2].c.result != None,
			weekdays[3].c.result != None,
			weekdays[4].c.result != None,
			weekdays[5].c.result != None,
			weekdays[6].c.result != None
		)
	).group_by(
		Test.id
	).order_by(
		weekdays[6].c.modified_utc.desc(),
		weekdays[5].c.modified_utc.desc(),
		weekdays[4].c.modified_utc.desc(),
		weekdays[3].c.modified_utc.desc(),
		weekdays[2].c.modified_utc.desc(),
		weekdays[1].c.modified_utc.desc(),
		weekdays[6].c.modified_utc.desc()
	)


def _get_crammers_subquery(filter_extension: str,
													 filter_user_uid: str,
													 filter_anonymous_token: str,
													 filter_name_uid: str,
													 crammers_expression,
													 since: datetime.datetime,
													 until: datetime.datetime,
													 tz_delta: datetime.timedelta):
	return database.session.query(
		Process.correct_count.label('process_correct_count'),
		Process.answer_time.label('process_answer_time'),
		Process.id.label('process_id'),
		Test.extension.label('test_extension'),
		Test.id.label('test_id'),
		Name.value.label('name_value'),
		Name.id.label('name_id'),
		(cast(crammers_expression, sqlalchemy.Integer)).label('crammers'),
		(Process.modified_utc).label('process_modified_utc')
	).join(
		Test
	).outerjoin(
		Name, Name.uid == Process.name_uid
	).filter(
		True if filter_extension is None else \
			Test.extension.ilike('%' + filter_extension + '%'),
		True if filter_user_uid is None else \
				filter_user_uid == Process.user_uid,
		True if filter_user_uid is not None or \
			filter_anonymous_token is not None else \
				Process.name_uid != None,
		Process.anonymous_token == filter_anonymous_token,
		True if filter_name_uid is None else \
			filter_name_uid == Process.name_uid,
		and_(
			Process.modified_utc >= since + tz_delta,
			Process.modified_utc < until + tz_delta
		) if since is not None else \
			Process.modified_utc < until + tz_delta,
		Test.deleted_utc == None
	).subquery()
