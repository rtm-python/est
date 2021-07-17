# -*- coding: utf-8 -*-

"""
Main module to run application.
"""

# Standard libraries import
import logging
import sys
import os

# Additional libraries import
import click
from flask.cli import AppGroup

# Append source path on wsgi initialization
sys.path.append('source')

# Application modules import
from blueprints import application
from models import database
from config import CONFIG
from plugins import PluginManager

# Additional flask cli commands
database_cli = AppGroup('run-database')

@application.cli.command('run-identica')
def run_identica():
	"""
	Run PluginManager to communicate with application identica bot.
	"""
	logging.getLogger().level = logging.INFO
	PluginManager(
		'identica', domain_url='https://crammer.scene.kz').execute('run')


@database_cli.command('export')
@click.argument('tables')
def run_database_export(tables: str):
	"""
	Run PluginManager to export database tables.
	"""
	logging.getLogger().level = logging.INFO
	PluginManager(
		'database',
		target_path=os.path.join(
			os.path.dirname(os.path.dirname(__file__)), 'csv'),
		table_list=tables.split(',')
	).execute('export_csv')


@database_cli.command('import')
@click.argument('tables')
def run_database_import(tables: str):
	"""
	Run PluginManager to import database tables.
	"""
	logging.getLogger().level = logging.INFO
	PluginManager(
		'database',
		target_path=os.path.join(
			os.path.dirname(os.path.dirname(__file__)), 'csv'),
		table_list=tables.split(',')
	).execute('import_csv')


# Add additional flask cli commands
application.cli.add_command(database_cli)


# Run application on executing module
if __name__ == '__main__':
	logging.getLogger().level = logging.DEBUG
	application.run(CONFIG['web']['host'], CONFIG['web']['port'])
