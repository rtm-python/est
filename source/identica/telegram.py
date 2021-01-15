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

# Application modules import

# Additional libraries import
import requests


url_telegram = 'https://api.telegram.org/bot%s/'
cmd_get_updates = 'getUpdates'
cmd_send_message = 'sendMessage'
cmd_delete_message = 'deleteMessage'
handle_thread = None
break_event = None
alphabet = string.ascii_lowercase + string.digits
data = {}


def handle(break_event: threading.Event, data: dict) -> None:
	"""
	Handle identica bot communication.
	"""
	clear_index = 15
	repeat_index = clear_index
	while not break_event.is_set():
		time.sleep(1)
		try:
			timestamp = datetime.datetime.utcnow().timestamp()
			response = requests.get(data['url_get_updates'] % data['offset'])
			response_dict = response.json()
			print(json.dumps(response_dict, indent=2))
			if response_dict.get('ok') is True:
				for item in response_dict['result']:
					if data['offset'] <= item['update_id']:
						data['offset'] = item['update_id'] + 1
					if item['message']['from']['is_bot'] is True:
						continue
					usercode = item['message']['text'].strip().lower()
					if len(usercode) != 4:
						continue
					response = requests.post(
						data['url_delete_message'],
						json={
							'chat_id': item['message']['chat']['id'],
							'message_id': item['message']['message_id']
						}
					)
					if data['usercodes'].get(usercode) is None:
						continue
					usercode_item = data['usercodes'][usercode]
					if usercode_item['valid_before'] < timestamp:
						continue
					usercode_item['from_id'] = item['message']['from']['id']
					usercode_item['chat_id'] = item['message']['chat']['id']
					usercode_item['passcode'] = \
						''.join(secrets.choice(alphabet) for i in range(4))
					usercode_item['name'] = ' '.join([
						item['message']['from']['first_name'],
						item['message']['from']['last_name']
					])
					response = requests.post(
						data['url_send_message'],
						json={
							'chat_id': usercode_item['chat_id'],
							'text': data['website'] + ':\n\n' + usercode_item['passcode']
						}
					)
					if response.json()['ok']:
						usercode_item['message_id'] = \
							response.json()['result']['message_id']
			repeat_index -= 1
			print(repeat_index)
			if repeat_index <= 0:
				# clear timed out passcodes
				repeat_index = clear_index
				timestamp = datetime.datetime.utcnow().timestamp()
				usercode_list = []
				for usercode in data['usercodes'].keys():
					if data['usercodes'][usercode]['valid_before'] < timestamp:
						usercode_list += [usercode]
				for usercode in usercode_list:
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
	break_event.clear()


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
		while break_event.is_set():
			time.sleep(1)
		break_event = None
		handle_thread.join()
		handle_thread = None


def init() -> None:
	"""
	Initiate data for identica bot communication.
	"""
	global data
	if data.get('token') is None or data.get('offset') is None:
		with open('source/identica/token.txt', 'r') as token_file:
			 token_data = token_file.read().strip()
		data['website'], data['token'] = token_data.split('\n')
		data['website'] = data['website'].strip()
		data['token'] = data['token'].strip()
		data['usercodes'] = {}
		data['url_get_updates'] = \
			url_telegram % data['token'] + cmd_get_updates + '?offset=%d'
		data['url_send_message'] = \
			url_telegram % data['token'] + cmd_send_message
		data['url_delete_message'] = \
			url_telegram % data['token'] + cmd_delete_message
		response = requests.get(data['url_get_updates']	% -1)
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
		usercode = ''.join(secrets.choice(alphabet) for i in range(4))
		if data['usercodes'].get(usercode) is None:
			break
	data['usercodes'][usercode] = {
		'passcode': None, 'name': None,
		'from_id': None, 'message_id': None,
		'valid_before': (
			datetime.datetime.utcnow() + datetime.timedelta(seconds=15)
		).timestamp()
	}
	return usercode


def verify_usercode(usercode: str, passcode: str) -> dict:
	"""
	Verify usercode and passcode pair,
	return usercode data assigned to user on success.
	"""
	if data['usercodes'].get(usercode) is not None:
		if data['usercodes'][usercode]['passcode'] is not None:
			timestamp = datetime.datetime.utcnow().timestamp()
			if data['usercodes'][usercode]['valid_before'] < timestamp:
				usercode_item = data['usercodes'][usercode]
			else:
				usercode_item = None
			del data['usercodes'][usercode]
			response = requests.post(
				data['url_delete_message'],
				json={
					'chat_id': usercode_item['chat_id'],
					'message_id': usercode_item['message_id']
				}
			)
			return usercode_item


if __name__ == '__main__':
	init()
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
	print(json.dumps(
		verify_usercode(usercode, data['usercodes'][usercode]['passcode']),
		indent=2
	))
