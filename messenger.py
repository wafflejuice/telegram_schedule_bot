import requests

from config import Config

class Telegram:
	GET_UPDATES_BASE_URL = 'https://api.telegram.org/bot{}/getUpdates'
	SEND_MESSAGE_BASE_URL = 'https://api.telegram.org/bot{}/sendMessage'
	
	LINE_BREAK = chr(10)
	
	@staticmethod
	def date_to_korean_format(YYYYMMDD):
		base_date = "{}년 {}월 {}일"
		
		return base_date.format(YYYYMMDD[0:4], YYYYMMDD[4:6], YYYYMMDD[6:8])
	
	@classmethod
	def args_to_message(cls, args):
		message = ''
		
		for arg in args:
			message = message + cls.LINE_BREAK + str(arg)
			
		return message
	
	@classmethod
	def args_to_update_message(cls, old_args, new_args):
		base_message = "<b>※UPDATED※</b>{0}{1}{0}{0}<i>에서</i>{0}{2}{0}{0}<i>로 변경</i>"
		
		old_text = cls.args_to_message(old_args)
		new_text = cls.args_to_message(new_args)
		
		return base_message.format(cls.LINE_BREAK, old_text, new_text)
	
	@classmethod
	def send_message(cls, chat_id, message):
		token = Config.load_config()['telegram']['token']
		send_message_url = cls.SEND_MESSAGE_BASE_URL.format(token)
		
		requests.get(send_message_url, params={'chat_id': chat_id, 'text': message, 'parse_mode': 'html'})
		
	@classmethod
	def send_messages(cls, chat_ids, message):
		for chat_id in chat_ids:
			cls.send_message(chat_id, message)