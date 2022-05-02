import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.firefox.options import Options
import threading
import datetime
import time
import sys

from config import Config
from database import MariaDB
from messenger import Telegram

class WatchTarget:
	@classmethod
	def update_schedule(cls):
		pass
	
	@classmethod
	def run_notifier(cls):
		update_schedule_thread = threading.Thread(target=cls.update_schedule)
		update_schedule_thread.start()

class President(WatchTarget):
	SCHEDULE_URL = 'https://www1.president.go.kr/calendar'
	
	@classmethod
	def update_schedule(cls):
		config = Config.load_config()
		chat_ids = config['telegram']['chat ids']
				
		db = MariaDB()
		
		db.connect(config['mariaDB']['host'], config['mariaDB']['port'], config['mariaDB']['user'], config['mariaDB']['passwd'])
		
		db.execute("CREATE DATABASE IF NOT EXISTS schedule")
		db.execute("USE schedule")
		db.execute("CREATE TABLE IF NOT EXISTS president(schedule_id INT PRIMARY KEY AUTO_INCREMENT, datetime DATETIME, place TEXT, name TEXT, participants TEXT)")
		db.execute("ALTER TABLE president CONVERT TO CHARSET UTF8")
		
		db.commit()
		
		options = Options()
		options.headless = True
		driver = webdriver.Firefox(executable_path='geckodriver', options=options)
		driver.implicitly_wait(2)
		
		try:
			while True:
				driver.get(cls.SCHEDULE_URL)
				
				elements = driver.find_elements_by_xpath('//td[@class="md-trigger caltd"]')
				for element in elements:
					fetched_date = element.get_attribute('data-cal')
					
					# is it async? should i wait until it(reponse to click) happens?
					element.click()
					
					while True:
						try:
							driver.find_elements_by_xpath('//table[@class="table"]/tbody')
							time.sleep(0.1)
						except StaleElementReferenceException:
							break

					trs = driver.find_elements_by_xpath('//table[@class="table"]/tbody/tr')
					
					# if there are many empty "md-trigger caltd" class, selenium waits all of them for loading.
					if not trs:
						continue
					
					# Fetched content format depends on screen size(PC, android, iphone ...). This program is recognized as PC.
					fetched_entries_count = len(trs)-1
					fetched_table = []
					fetched_lines = ['대통령 일정', fetched_date]
					
					for tri in range(len(trs)):
						if tri == 0:
							continue
							
						tds = trs[tri].find_elements_by_xpath('td')
						
						fetched_datetime = datetime.datetime.strptime("{} {}".format(fetched_date, tds[0].text), "%Y-%m-%d %H:%M")
						fetched_table.append((fetched_datetime, tds[1].text, tds[2].text, tds[3].text))
						
						fetched_line = Telegram.args_to_message(['시간 : ' + fetched_datetime.strftime("%H:%M"),
																 '장소 : ' + tds[1].text,
																 '일정명 : ' + tds[2].text,
																 '참석자 : ' + tds[3].text])
						fetched_lines.append(fetched_line)
						
					existing_entries_count = db.execute("SELECT datetime, place, name, participants FROM president WHERE DATE(datetime)=DATE(%s) ORDER BY datetime ASC", (fetched_date,))
					
					# new schedules!
					if existing_entries_count == 0:
						for yi in range(fetched_entries_count):
							fetched_values = (fetched_table[yi][0], fetched_table[yi][1],  fetched_table[yi][2], fetched_table[yi][3])
							db.execute("INSERT INTO president(datetime, place, name, participants) VALUES (%s, %s, %s, %s)", fetched_values)
						
						db.commit()
						
						new_schedule_message = Telegram.args_to_message(fetched_lines)
						Telegram.send_messages(chat_ids, new_schedule_message)
						
					# schedules already exist at that day
					else:
						existing_table = db.fetch_all()
						compare_result = cls.compare_2d_arrays(existing_table, fetched_table)
						
						if not compare_result:
							db.execute("DELETE FROM president WHERE DATE(datetime)=DATE(%s)", (fetched_date,))
							existing_lines = ['대통령 일정', fetched_date]
							
							for yi in range(len(existing_table)):
								existing_line = Telegram.args_to_message(['시간 : ' + existing_table[yi][0].strftime('%H:%M'),
																		  '장소 : ' + existing_table[yi][1],
																		  '일정명 : ' + existing_table[yi][2],
																		  '참석자 : ' + existing_table[yi][3]])
								existing_lines.append(existing_line)
							
							for yi in range(fetched_entries_count):
								fetched_values = (fetched_table[yi][0], fetched_table[yi][1], fetched_table[yi][2], fetched_table[yi][3])
								db.execute("INSERT INTO president(datetime, place, name, participants) VALUES (%s, %s, %s, %s)", fetched_values)
								
							db.commit()
							
							update_schedule_message = Telegram.args_to_update_message(existing_lines, fetched_lines)
							Telegram.send_messages(chat_ids, update_schedule_message)
							
				time.sleep(30)
		finally:
			driver.quit()
	
	@staticmethod
	def compare_2d_arrays(table1, table2):
		table1_entries_count = len(table1)
		table2_entries_count = len(table2)
		
		if table1_entries_count != table2_entries_count:
			return False
		
		return list(table1) == list(table2)
	
	
class Minjoo(WatchTarget):
	SCHEDULE_URL = 'https://theminjoo.kr/schedule'
	NO_SCHEDULE = '등록된 일정이 없습니다.'
	
	@classmethod
	def update_schedule(cls):
		config = Config.load_config()
		chat_ids = config['telegram']['chat ids']
		
		db = MariaDB()
		
		db.connect(config['mariaDB']['host'], config['mariaDB']['port'], config['mariaDB']['user'], config['mariaDB']['passwd'])
		
		db.execute("CREATE DATABASE IF NOT EXISTS schedule")
		db.execute("USE schedule")
		db.execute("CREATE TABLE IF NOT EXISTS minjoo(schedule_id INT PRIMARY KEY AUTO_INCREMENT, date DATE, content TEXT)")
		db.execute("ALTER TABLE minjoo CONVERT TO CHARSET UTF8")
		
		db.commit()
		
		while True:
			try:
				response = requests.get(cls.SCHEDULE_URL, timeout=10)
			except requests.exceptions.RequestException as e:
				print(e, file=sys.stderr)
				
				continue
				
			html = response.text
			soup = BeautifulSoup(html, 'html.parser')
			
			for schedule_cnt in soup.find_all(class_='schedule_cnt'):
				fetched_date = str(schedule_cnt.get('id')).split('_')[1]
				fetched_datetime = datetime.datetime.strptime(fetched_date, "%Y%m%d")
				schedule = str(schedule_cnt.get_text()).strip()
				
				count = db.execute("SELECT content FROM minjoo WHERE DATE(date)=DATE(%s)", (fetched_datetime.strftime('%Y-%m-%d'),))
				
				'''
				situation	|	existing content	|	fetched content				|	action
				------------|-----------------------+-------------------------------+-------------------------------
				1-1.		|	No data				|	No schedule					|	insert
				1-2.		|	No data				|	Schedule exists				|	insert, send new message
				2-1.		|	No schedule			|	No schedule					|	-
				2-2.		|	No schedule			|	Schedule exists				|	update, send new message
				3-1.		|	Schedule exists		|	No schedule					|	update, send update message
				3-2.		|	Schedule exists		|	Schedule exists (same)		|	-
				3-3.		|	Schedule exists		|	Schedule exists (different)	|	update, send update message
				'''
				
				# situation 1.
				if count == 0:
					# situation 1-1. & situation 1-2.
					db.execute("INSERT INTO minjoo (date, content) VALUES (%s, %s)", (fetched_datetime, schedule))
					
					# situation 1-2.
					if schedule != cls.NO_SCHEDULE:
						schedule_message = Telegram.args_to_message((Telegram.date_to_korean_format(fetched_date), schedule))
						Telegram.send_messages(chat_ids, schedule_message)
				# situation 2. & situation 3.
				else:
					existing_schedule = db.fetch_one()[0]
					
					# situation 2.
					if existing_schedule == cls.NO_SCHEDULE:
						# situation 2-1.
						if schedule == cls.NO_SCHEDULE:
							pass
						# situation 2-2.
						else:
							db.execute("UPDATE minjoo SET content=%s WHERE DATE(date)=DATE(%s)", (schedule, fetched_datetime))
							schedule_message = Telegram.args_to_message((Telegram.date_to_korean_format(fetched_date), schedule))
							Telegram.send_messages(chat_ids, schedule_message)
					# situation 3.
					else:
						# situation 3-2.
						if schedule == existing_schedule:
							pass
						# situation 3-1. & situation 3-3.
						else:
							db.execute("UPDATE minjoo SET content=%s WHERE DATE(date)=DATE(%s)", (schedule, fetched_datetime))
							old_args = (Telegram.date_to_korean_format(fetched_date), existing_schedule)
							new_args = (Telegram.date_to_korean_format(fetched_date), schedule)
							updated_schedule_message = Telegram.args_to_update_message(old_args, new_args)
							Telegram.send_messages(chat_ids, updated_schedule_message)
			
			db.commit()
			
			time.sleep(30)
