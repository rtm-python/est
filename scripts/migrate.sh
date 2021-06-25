#!/usr/bin/env bash

export FLASK_APP=source/run.py \
	&& . .venv/bin/activate

[ ! -d database ] \
	&& mkdir database \
	&& echo 'Folder "database" - created!' \
	&& flask db init

flask db migrate \
	&& flask db upgrade \
	&& echo 'Database "est.db" - migrated!' \
	&& deactivate
