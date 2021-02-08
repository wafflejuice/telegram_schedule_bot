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
			MariaDB().execute("SELECT schedule from minjoo where date='{}'".format(date))
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
	def date_to_korean_format(date):
		base_date = "{}년 {}월 {}일"
		
		return base_date.format(date[0:4], date[4:6], date[6:8])
	
	@staticmethod
	def text_to_message(date, text):
		return Telegram.date_to_korean_format(date) + chr(10) + text

	@staticmethod
	def updated_text_to_message(date, existing_text, update_text):
		base_message = "<b>※UPDATED※</b>{0}{0}{1}{0}{2}{0}<i>에서</i>{0}{3}{0}<i>로 변경</i>"
		
		return base_message.format(chr(10), Telegram.date_to_korean_format(date), existing_text, update_text)