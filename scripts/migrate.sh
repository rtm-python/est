#!/usr/bin/env bash

export FLASK_APP=source/run.py \
	&& . .venv/bin/activate \
	&& flask db migrate \
	&& flask db upgrade \
	&& echo 'Database "est.db" - migrated!' \
	&& deactivate
