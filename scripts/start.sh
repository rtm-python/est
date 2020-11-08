#!/usr/bin/env bash

for service in $(basename -a $(ls -a config/*.service));
do
	cp config/"$service" /etc/systemd/system/"$service" \
		&& systemctl start "$service" \
		&& systemctl enable "$service" \
		&& echo 'Unit '"$service"' - Copied, started and enabled!'
done
