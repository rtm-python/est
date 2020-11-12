# -*- coding: utf-8 -*-

'''
Store module for Examination entity.
'''

# Application modules import
from models import database
from models import count
from models.entity.examination import Examination


def create_examination(name: str, description: str,
											 plugin: str, plugin_options: str,
											 default_repeat: int, default_performance: int
											 ) -> Examination:
	"""
	Create examination and return created entity.
	"""
	examination = Examination(name, description,
    												plugin, plugin_options,
														default_repeat, default_performance)
	database.session.add(examination)
	database.session.commit()
	return examination


def read_examination(uid: str) -> Examination:
	"""
	Return examination entity by uid.
	"""
	return Examination.query.filter_by(uid=uid).first()


def update_examination(uid: str, name: str, description: str,
											 plugin: str, plugin_options: str,
											 default_repeat: int, default_performance: int
											 ) -> Examination:
	'''
	Update examination and return updated entity.
	'''
	examination = read_examination(uid)
	examination.name = name
	examination.description = description
	examination.plugin = plugin
	examination.plugin_options = plugin_options
	examination.default_repeat = default_repeat
	examination.default_performance = default_performance
	examination.set_modified()
	database.session.commit()


def delete_examination(uid: str) -> Examination:
	'''
	Delete examination by set_deleted and return deleted entity.
	'''
	examination = read_examination(uid)
	examination.set_deleted()
	database.session.commit()


def _get_list_query(filter_name: str, filter_plugin: str,
										filter_hide_global: bool
										):
	"""
	Return query object fo examination based on arguments.
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


def read_examination_list(offset: int, limit: int,
													filter_name: str, filter_plugin: str,
													filter_hide_global: bool
													) -> [tuple]:
	"""
	Return filtered list of dictionaries filled with entity fields.
	"""
	return _get_list_query(
		filter_name, filter_plugin, filter_hide_global
	).limit(limit).offset(offset).all()


def count_examination_list(filter_name: str, filter_plugin: str,
													 filter_hide_global: bool
													 ) -> int:
	"""
	Return items number in filtered list of entities.
	"""
	return count(_get_list_query(
		filter_name, filter_plugin, filter_hide_global))
