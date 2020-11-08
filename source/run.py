# -*- coding: utf-8 -*-

from flask import Flask


application = Flask('hw')

@application.route('/')
def home():
	return 'Hello World'


if __name__ == '__main__':
	application.run()
