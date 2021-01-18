# -*- coding: utf-8 -*-

"""
Blueprint module to handle identica_bot communication.
"""

# Standard libraries import
import secrets
import string
import threading
import time
import json
import datetime
import logging
import os

# Additional libraries import
import requests

# Global Constants
filename = 'source/identica/telegram.txt'
url_telegram = 'https://api.telegram.org/bot%s/'
cmd_get_updates = 'getUpdates'
cmd_send_message = 'sendMessage'
cmd_delete_message = 'deleteMessage'
alphabet = string.ascii_lowercase + string.digits
code_length = 4
clear_index = 120
valid_seconds = 15
sleep_seconds = 3
message_limit = 100

# Global Variables
handle_thread = None
break_event = None
data = {}


def handle(break_event: threading.Event, data: dict) -> None:
	"""
	Handle identica bot communication.
	"""
	repeat_index = clear_index
	# Main function (thead) loop
	while not break_event.is_set():
		time.sleep(sleep_seconds) # prevent processor overload
		try:
			timestamp = datetime.datetime.utcnow().timestamp()
			response = requests.get(data['url_get_updates'] % \
				(data['offset'], message_limit))
			response_dict = response.json()
			if response_dict.get('ok') is True:
				# Request is successful (response with result)
				for item in response_dict['result']:
					if data['offset'] <= item['update_id']:
						data['offset'] = item['update_id'] + 1
					if item['message']['from']['is_bot'] is True:
						logging.warning(
							'Ignoring message from bot: %s' % \
							 item['message']['from']['id']
						)
						continue # skip to next on bot messages
					usercode = item['message']['text'].strip().lower()
					if len(usercode) != code_length:
						logging.warning(
							'Ignoring invalid usercode: %s' % usercode
						)
						continue # skip to next on mismatch by code length
					if data['usercodes'].get(usercode) is None:
						logging.warning(
							'Ignoring not existing usercode: %s' % usercode
						)
						continue # skip to next on usercode not found
					usercode_item = data['usercodes'][usercode]
					if usercode_item['valid_before'] < timestamp:
						logging.warning(
							'Ignoring timed out for %d seconds usercode: %s' % \
							(timestamp - usercode_item['valid_before'], usercode)
						)
						del data['usercodes'][usercode]
						continue # skip to next on invalid timestamp
					# Fill passing userdata
					usercode_item['from_id'] = item['message']['from']['id']
					usercode_item['chat_id'] = item['message']['chat']['id']
					usercode_item['name'] = ' '.join([
						item['message']['from']['first_name'],
						item['message']['from']['last_name']
					])
					usercode_item['passcode'] = \
						''.join(secrets.choice(alphabet) for i in range(code_length))
					# Send passcode within chat message
					response = requests.post(
						data['url_send_message'],
						json={
							'chat_id': usercode_item['chat_id'],
							'text': data['website'] + ':\n\n' + usercode_item['passcode']
						}
					)
					# Store message_id for futher deleting
					if response.json()['ok']:
						usercode_item['message_id'] = \
							response.json()['result']['message_id']
					# Delete correct usercode message
					response = requests.post(
						data['url_delete_message'],
						json={
							'chat_id': item['message']['chat']['id'],
							'message_id': item['message']['message_id']
						}
					)
			repeat_index -= 1
			if repeat_index <= 0:
				# Clear timed out usercodes
				repeat_index = clear_index
				usercode_list = [] # list of usercode (keys) to delete
				for usercode in data['usercodes'].keys():
					if data['usercodes'][usercode]['valid_before'] < timestamp:
						usercode_list += [usercode]
				# Iterate over usercodes to delete list item and message
				for usercode in usercode_list:
					if data['usercodes'][usercode].get('chat_id') is not None:
						response = requests.post(
							data['url_delete_message'],
							json={
								'chat_id': data['usercodes'][usercode]['chat_id'],
								'message_id': data['usercodes'][usercode]['message_id']
							}
						)
					del data['usercodes'][usercode]
		except:
			logging.error('Identica bot communication error', exc_info=1)
	break_event.clear() # Indicate on thread function exiting


def run() -> None:
	"""
	Run in thread handling identica bot communication.
	"""
	global handle_thread
	global break_event
	global data
	if handle_thread is None or break_event is None:
		break_event = threading.Event()
		handle_thread = threading.Thread(
			target=handle, args=(break_event, data))
		handle_thread.start()


def stop() -> None:
	"""
	Stop thread with handling identica bot communication.
	"""
	global handle_thread
	global break_event
	if handle_thread is not None and break_event is not None:
		break_event.set()
		while break_event.is_set(): # Wait for thread function exit
			time.sleep(1)
		break_event = None
		handle_thread.join()
		handle_thread = None


def init(hidden: bool = True) -> None:
	"""
	Initiate data for identica bot communication.
	"""
	global data
	if data.get('token') is None or data.get('offset') is None:
		# Read initiating data from file (name and token)
		with open(filename, 'r') as telegram_file:
			 telegram_data = telegram_file.read().strip()
		if hidden:
			os.remove(filename)
		# Initiate shareable  data dictionary
		data['website'], data['token'] = telegram_data.split('\n')
		data['website'] = data['website'].strip()
		data['token'] = data['token'].strip()
		data['usercodes'] = {}
		data['url_get_updates'] = \
			url_telegram % data['token'] + cmd_get_updates + \
			'?offset=%d&limit=%d'
		data['url_send_message'] = \
			url_telegram % data['token'] + cmd_send_message
		data['url_delete_message'] = \
			url_telegram % data['token'] + cmd_delete_message
		# Initial update messages from communication server
		response = requests.get(data['url_get_updates']	% (-1, 1))
		response_dict = response.json()
		if response_dict.get('ok') is True:
			if data.get('offset') is None:
				data['offset'] = 0
			for item in response_dict['result']:
				if data['offset'] < item['update_id']:
					data['offset'] = item['update_id'] + 1


def create_usercode() -> str:
	"""
	Create and return usercode for user.
	"""
	while True:
		usercode = ''.join(secrets.choice(alphabet) \
											 for i in range(code_length))
		if data['usercodes'].get(usercode) is None:
			break # dublicates not found (success)
	# Create usercode data item
	data['usercodes'][usercode] = {
		'passcode': None, 'name': None,
		'from_id': None, 'message_id': None,
		'valid_before': (
			datetime.datetime.utcnow() + datetime.timedelta(seconds=valid_seconds)
		).timestamp()
	}
	return usercode


def verify_usercode(usercode: str, passcode: str) -> dict:
	"""
	Verify usercode and passcode pair,
	return usercode data on success.
	"""
	if data['usercodes'].get(usercode) is not None:
		if data['usercodes'][usercode]['passcode'] is not None:
			if data['usercodes'][usercode]['valid_before'] < \
					datetime.datetime.utcnow().timestamp():
				usercode_item = data['usercodes'][usercode]
			else:
				usercode_item = None # indvalid (timed out) usercode
			# Delete used usercode data and message
			response = requests.post(
				data['url_delete_message'],
				json={
					'chat_id': usercode_item['chat_id'],
					'message_id': usercode_item['message_id']
				}
			)
			del data['usercodes'][usercode]
			return usercode_item


def send_message(chat_id: int, message: str) -> None:
	"""
	Send message to chat by chat_id.
	"""
	response = requests.post(
		data['url_send_message'],
		json={'chat_id': chat_id,	'text': message}
	)


if __name__ == '__main__':
	init(False)
	usercode = create_usercode()
	print(usercode)

	run()
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		pass
	stop()

	print(json.dumps(data, indent=2))
	usercode_item = verify_usercode(usercode, data['usercodes'][usercode]['passcode'])
	if usercode_item is not None:
		print(json.dumps(usercode_item,	indent=2))
		if usercode_item['chat_id'] is not None:
			send_message(usercode_item['chat_id'], 'Добро пожаловать!')
