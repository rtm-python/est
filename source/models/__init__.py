# -*- coding: utf-8 -*-

"""
Initial module to initiate database models and migrations.
"""

# Standard libraries import
import os

# Additional libraries import
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Application modules import
from config import config
from blueprints import application

# Initiate database
database_folder = os.path.join(os.path.abspath(os.curdir), 'database')
print(database_folder)
if config['database']['filename'] is None:
	application.config['SQLALCHEMY_DATABASE_URI'] = config['database']['URI']
else:
	application.config['SQLALCHEMY_DATABASE_URI'] = config['database']['URI'] + \
		os.path.join(database_folder, config['database']['filename'])
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
database = SQLAlchemy(application)
migrate = Migrate(application, database, directory=database_folder)

# Entity modules import (prevent circular import)
from models.entity import user
from models.entity import test
from models.entity import process
from models.entity import task
