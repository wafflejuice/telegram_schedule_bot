from bs4 import BeautifulSoup
import requests
import json
import pymysql
import time

import privacy.telegram_privacy as telegram_privacy
import url

def initialize_db(cursor):
	cursor.execute("CREATE DATABASE IF NOT EXISTS minjoo_schedule_db")
	cursor.execute("USE minjoo_schedule_db")
	cursor.execute("CREATE TABLE IF NOT EXISTS minjoo_schedule_table(id VARCHAR(20) PRIMARY KEY, text TEXT)")
	cursor.execute("ALTER TABLE minjoo_schedule_table CONVERT TO CHARSET UTF8")

def date_to_korean_format(date):
	base_date = "{}년 {}월 {}일"
	
	return base_date.format(date[0:4], date[4:6], date[6:8])

def text_to_message(date, text):
	return date_to_korean_format(date) + chr(10) + text

def updated_text_to_message(date, existing_text, update_text):
	base_message = "<b>※UPDATED※</b>{0}{0}{1}{0}{2}{0}<i>에서</i>{0}{3}{0}<i>로 변경</i>"
	
	return base_message.format(chr(10), date_to_korean_format(date), existing_text, update_text)

def run():
	db = pymysql.connect(host='localhost', port=3306, user='YOUR USER', passwd='YOUR PASSWORD', charset='utf8')
	cursor = db.cursor()
	
	initialize_db(cursor)
	
	get_updates_url = url.get_updates_url.format(telegram_privacy.token)
	send_message_url = url.send_message_url.format(telegram_privacy.token)
	
	chat_id = json.loads(requests.get(get_updates_url).text)['result'][-1]['message']['from']['id']
	
	response = requests.get(url.schedule_url)
	html = response.text
	soup = BeautifulSoup(html, 'html.parser')
	
	# TODO: convert into async code
	while True:
		for schedule in soup.find_all(class_='schedule_cnt'):
			id = str(schedule.get('id'))
			date = id.split('_')[1]
			text = str(schedule.get_text()).strip()
			
			count = cursor.execute("SELECT * FROM minjoo_schedule_table WHERE id='{}'".format(id))
			if count == 0:
				cursor.execute("INSERT INTO minjoo_schedule_table (id, text) VALUES ('{}', '{}')".format(id, text))
				
				if text != '등록된 일정이 없습니다.':
					requests.get(send_message_url, params={'chat_id': chat_id, 'text': text_to_message(date, text), 'parse_mode':'html'})
			else:
				cursor.execute("SELECT text from minjoo_schedule_table where id='{}'".format(id))
				existing_text = cursor.fetchone()[0]
				if existing_text != text:
					cursor.execute("UPDATE minjoo_schedule_table SET text='{}' WHERE id='{}'".format(text, id))
					requests.get(send_message_url, params={'chat_id': chat_id, 'text': updated_text_to_message(date, existing_text, text), 'parse_mode':'html'})
		
		db.commit()
		
		time.sleep(60)