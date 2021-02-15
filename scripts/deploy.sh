#!/usr/bin/env bash

# Configuration

[ ! -d config ] \
	&& mkdir config \
	&& echo 'Folder "config" - created!'

[ -f config/app.json ] \
	&& yes | cp config/app.json config/_app.json \
	&& echo 'File "config/_app.json" - backup created!'

config=$(jq '.data[] | select(.version == "'$*'")' deployment.json)
if [ -z "$config" ];
then
	echo 'Define configuration version!' \
		&& exit
fi
echo "$config" > config/app.json \
	&& echo 'File "config/app.json" for "'"$*"'" - created!'

# Virtual Environment

[ -d .venv ] \
	&& yes | rm -r .venv \
	&& echo 'Virtual environment ".venv" - existing removed!'

python3 -m venv .venv \
	&& echo 'Virtual environment ".venv" - created!' \
	&& . .venv/bin/activate \
	&& pip install --upgrade pip \
	&& pip install -r requirements.txt \
	&& echo 'Virtual environment ".venv" - requirements installed!' \
	&& deactivate

# Database

[ ! -d database ] \
	&& mkdir database \
	&& echo 'Folder "database" - created!'

export FLASK_APP=source/run.py \
	&& . .venv/bin/activate \
	&& flask db init \
	&& flask db migrate \
	&& flask db upgrade \
	&& echo 'Database "est.db" - initiated!' \
	&& deactivate

# Serivce (WSGI)

name=$(jq -r '.name' deployment.json)
desc=$(jq -r '.desc' deployment.json)

jq -r '.wsgi[]' deployment.json > config/app.ini \
	&& echo 'WSGI "app.ini" - created!'

output=$(jq -r '.service[]' deployment.json) \
	&& output=${output/\$desc/"$desc"} \
	&& output=${output/\$user/$(whoami)} \
	&& output=${output/\$workdir/$(pwd)} \
	&& output=${output/\$bindir/$(pwd)"/.venv/bin"} \
	&& output=${output/\$exec/$(pwd)"/.venv/bin/uwsgi --ini config/app.ini"} \
	&& echo "$output" > config/"$name".service \
	&& echo 'Unit '"$name"'.service" - created!'

# Serivce (identica)

name='identica'
desc='handle identica bot messages'

output=$(jq -r '.service[]' deployment.json) \
	&& output=${output/\$desc/"$desc"} \
	&& output=${output/\$user/$(whoami)} \
	&& output=${output/\$workdir/$(pwd)} \
	&& output=${output/\$bindir/$(pwd)"/.venv/bin"} \
	&& output=${output/\$exec/$(pwd)"/.venv/bin/python source/identica/telegram.py"} \
	&& echo "$output" > config/"$name".service \
	&& echo 'Unit '"$name"'.service" - created!'

# Clear deployment

[ -f deployment.json ] \
	&& yes | rm deployment.json \
	&& echo 'Complete!'
