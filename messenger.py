import requests
import time
import re

from database import MariaDB
from config import Config

class Telegram:
	TELEGRAM_GET_UPDATES_BASE_URL = 'https://api.telegram.org/bot{}/getUpdates'
	TELEGRAM_SEND_MESSAGE_BASE_URL = 'https://api.telegram.org/bot{}/sendMessage'
	
	@staticmethod
	def send_message(chat_id, message):
		token = Config.load_config()['telegram']['token']
		send_message_url = Telegram.TELEGRAM_SEND_MESSAGE_BASE_URL.format(token)
		
		requests.get(send_message_url, params={'chat_id': chat_id, 'text': message, 'parse_mode': 'html'})
	
	@staticmethod
	def send_messages(chat_ids, message):
		for chat_id in chat_ids:
			Telegram.send_message(chat_id, message)

	@staticmethod
	def organize_message(writer, datetime, text):
		return writer + chr(10) + datetime.isoformat() + chr(10) + text
	
	@staticmethod
	def start(update, context):
		context.bot.send_message(chat_id=update.effective_chat.id, text="bot start")
	
	@staticmethod
	def echo(update, context):
		text_lower = update.message.text.lower()
		
		def select_schedule_by_date(date):
			MariaDB().execute("SELECT schedule FROM minjoo WHERE date='{}'".format(date))
			return MariaDB().fetch_one()[0]
		
		# retrieve available schedules from today
		if text_lower == 'gov':
			date_str = time.strftime('%Y%m%d', time.localtime(time.time()))
			for i in range(int(date_str), int(date_str) + 10):
				schedule = select_schedule_by_date(date_str)
				
				if schedule:
					update.message.reply_text(schedule)
				else:
					break
					
		elif text_lower.startswith('gov'):
			date_str = None
			
			if re.match('gov20[2-9][0-9][0-1][0-9][0-3][0-9]', text_lower):
				date_str = text_lower[3:11]
			elif re.match('gov[2-9][0-9][0-1][0-9][0-3][0-9]', text_lower):
				date_str = '20'+text_lower[3:9]
			elif re.match('gov[0-1][0-9][0-3][0-9]', text_lower):
				date_str = time.strftime('%Y', time.localtime(time.time())) + text_lower[3:7]
			
			schedule = select_schedule_by_date(date_str)
			update.message.reply_text(schedule if not schedule else "No data")
			
		else:
			update.message.reply_text("Invalid input")
			
			
	@staticmethod
	def date_to_korean_format(YYYYMMDD_str):
		base_date = "{}년 {}월 {}일"
		
		return base_date.format(YYYYMMDD_str[0:4], YYYYMMDD_str[4:6], YYYYMMDD_str[6:8])
	
	@staticmethod
	def text_to_message(lines):
		message = ''
		
		for arg in lines:
			message = message + chr(10) + str(arg)
			
		return message
	
	@classmethod
	def text_to_update_message(cls, old_lines, new_lines):
		base_message = "<b>※UPDATED※</b>{0}{1}{0}{0}<i>에서</i>{0}{2}{0}{0}<i>로 변경</i>"
		
		old_text = cls.text_to_message(old_lines)
		new_text = cls.text_to_message(new_lines)
		
		return base_message.format(chr(10), old_text, new_text)