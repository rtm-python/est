#!/usr/bin/env bash

cd config \
	&& ausearch -c '('"$*"')' --raw | audit2allow -M "$*"-rule \
	&& semodule -X 300 -i "$*"-rule.pp \
	&& setenforce permissive \
	&& setenforce enforcing \
	&& cd ..
