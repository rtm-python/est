#!/usr/bin/env bash

for service in $(basename -a $(ls -a config/*.service));
do
	systemctl stop "$service"
	systemctl disable "$service"
	yes | rm /etc/systemd/system/"$service" \
		&& echo 'Unit '"$service"' - Stopped, disabled and removed!'
done
