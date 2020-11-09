# -*- coding: utf-8 -*-

"""
Initial base blueprint module to handle basic routes.
"""

# Standard libraries import
import logging
import os
import sys

# Application modules import
from config import config
from config import UrlPrefix
from blueprints import application

# Additional libraries import
from flask import Blueprint

# Initiate Blueprint object
blueprint = Blueprint(
	'base', __name__,
	static_folder='',
	template_folder=''
)


# HTTP_400_BAD_REQUEST
# HTTP_401_UNAUTHORIZED
# HTTP_403_FORBIDDEN
# HTTP_404_NOT_FOUND
# HTTP_405_METHOD_NOT_ALLOWED
# HTTP_406_NOT_ACCEPTABLE
# HTTP_408_REQUEST_TIMEOUT
# HTTP_409_CONFLICT
# HTTP_410_GONE
# HTTP_411_LENGTH_REQUIRED
# HTTP_412_PRECONDITION_FAILED
# HTTP_413_REQUEST_ENTITY_TOO_LARGE
# HTTP_414_REQUEST_URI_TOO_LONG
# HTTP_415_UNSUPPORTED_MEDIA_TYPE
# HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
# HTTP_417_EXPECTATION_FAILED
# HTTP_428_PRECONDITION_REQUIRED
# HTTP_429_TOO_MANY_REQUESTS
# HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE
# HTTP_500_INTERNAL_SERVER_ERROR
# HTTP_501_NOT_IMPLEMENTED
# HTTP_502_BAD_GATEWAY
# HTTP_503_SERVICE_UNAVAILABLE
# HTTP_504_GATEWAY_TIMEOUT
# HTTP_505_HTTP_VERSION_NOT_SUPPORTED
@application.errorhandler(400)
@application.errorhandler(401)
@application.errorhandler(403)
@application.errorhandler(404)
@application.errorhandler(405)
@application.errorhandler(406)
@application.errorhandler(408)
@application.errorhandler(409)
@application.errorhandler(410)
@application.errorhandler(411)
@application.errorhandler(412)
@application.errorhandler(413)
@application.errorhandler(414)
@application.errorhandler(415)
@application.errorhandler(416)
@application.errorhandler(417)
@application.errorhandler(428)
@application.errorhandler(429)
@application.errorhandler(431)
@application.errorhandler(500)
@application.errorhandler(501)
@application.errorhandler(502)
@application.errorhandler(503)
@application.errorhandler(504)
@application.errorhandler(505)
def error_handler(error):
	"""
	Return error message.
	"""
	logging.debug(error)
	error_code = getattr(error, 'code', 0)
	return str(error_code), \
		error_code if 400 <= error_code < 500 else 200


@blueprint.route('/', methods=('GET',))
def landing():
	"""
	Return landing page.
	"""
	logging.debug('LANDING')
	return 'Landing Page', 200


## Register blueprint
#application.register_blueprint(
#	blueprint,
#	url_prefix=UrlPrefix.BASE.value
#)



#logging.debug(
#	"\r\n".join(
#		[
#			"%s = %s" % (key, getattr(blueprint, key)) \
#				if key[:1] != '_' else '' \
#					for key in dir(blueprint)
#		]
#	)
#)
