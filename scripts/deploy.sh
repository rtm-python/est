#!/usr/bin/env bash

# Configuration

[ ! -d config ] \
	&& mkdir config \
	&& echo 'Folder "config" - created!'

[ -f config/app.json ] \
	&& yes | cp config/app.json config/_app.json \
	&& echo 'File "config/_app.json" - backup created!'

config=$(jq '.data[] | select(.version == "'$*'")' secrets/deployment.json)
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

# Serivce (WSGI)

name=$(jq -r '.name' secrets/deployment.json)
desc=$(jq -r '.desc' secrets/deployment.json)

jq -r '.wsgi[]' secrets/deployment.json > config/app.ini \
	&& echo 'WSGI "app.ini" - created!'

output=$(jq -r '.service[]' secrets/deployment.json) \
	&& output=${output/\$desc/"$desc"} \
	&& output=${output/\$user/$(whoami)} \
	&& output=${output/\$workdir/$(pwd)} \
	&& output=${output/\$bindir/$(pwd)"/.venv/bin"} \
	&& output=${output/\$exec/$(pwd)"/.venv/bin/uwsgi --ini config/app.ini"} \
	&& echo "$output" > config/"$name".service \
	&& echo 'Unit '"$name"'.service" - created!'
