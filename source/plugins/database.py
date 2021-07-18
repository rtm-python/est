# -*- coding: utf-8 -*-

"""
Module to handle database plugin.
"""

# Standard libraries import
import os
import csv
import logging
import datetime
import uuid

# Application modules import
from models import database

# Additional libraries import
import sqlalchemy


class Plugin():
	"""
	This Plugin class describes importing/exporting data to/form database.
	"""
	target_path = None
	table_list = None

	def __init__(self, target_path: str, table_list: list) -> "Plugin":
		"""
		Initiate Plugin object.
		"""
		self.target_path = target_path
		self.table_list = table_list

	def export_csv(self) -> None:
		"""
		Export data from database.
		"""
		metadata = sqlalchemy.MetaData()
		metadata.bind = database.engine
		for table in self.table_list:
			sql_table = sqlalchemy.Table(table, metadata, autoload=True)
			sql_select = sqlalchemy.sql.select([sql_table])
			with database.engine.connect() as connection:
				sql_result = connection.execute(sql_select)
				csv_filepath = os.path.join(self.target_path, '%s.csv' % table)
				with open(csv_filepath, 'w') as csv_file:
					csv_writer = csv.writer(csv_file)
					csv_writer.writerow(sql_result.keys())
					csv_writer.writerows(sql_result)
			print('Table "%s" exported to "%s"' % (table, csv_filepath))

	def import_csv(self) -> None:
		"""
		Import data to database.
		"""
		metadata = sqlalchemy.MetaData()
		metadata.bind = database.engine
		for table in self.table_list:
			sql_table = sqlalchemy.Table(table, metadata, autoload=True)
			sql_insert = sql_table.insert()
			with database.engine.connect() as connection:
				csv_filepath = os.path.join(self.target_path, '%s.csv' % table)
				with open(csv_filepath, 'r') as csv_file:
					csv_dict_reader = csv.DictReader(csv_file)
					connection.execute(
						sql_insert, [cast_row_values(row) for row in csv_dict_reader]
					)
			print('Table "%s" imported from "%s"' % (table, csv_filepath))


def cast_row_values(row: dict) -> dict:
	"""
	Cast row values (datetime).
	"""
	for key, value in row.items():
		if len(value) == 0:
			row[key] = None
		elif value == 'True' or value == 'False':
			row[key] = bool(value)
		elif key.endswith('_utc') or key.endswith('_local'):
			if len(value) == 26:
				row[key] = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
			elif len(value) == 19:
				row[key] = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
	row['is_deleted'] = bool(row['deleted_utc'] is not None)
	return row
