import os
import requests
import time
import telebot
import json
from webserver import keepAlive

id_mesh = os.environ['id_m']
id_t = os.environ['id_t']
token = os.environ['token']
bot_token = os.environ['bot_token']
url = f"https://dnevnik.mos.ru/mobile/api/notifications/search?student_id={id_mesh}"
mark_url = f"https://dnevnik.mos.ru/reports/api/progress/json?academic_year_id=9&student_profile_id={id_mesh}"
cache = []

keepAlive()
bot = telebot.TeleBot(bot_token)
has_new_info = False
while True:
  with open('Cache.json') as json_file:
    cache = json.load(json_file)
  response = requests.get(url,  headers = {
    'Auth-Token': token
  }).json()
  for i in response:
    if not i in cache:
      has_new_info = True
      break
  if has_new_info:
    to_print = []
    for i in range(len(response) - 1, -1, -1):
      if response[i] in cache:
        continue
      else:
        to_print.append(response[i])
        cache.append(response[i])
    for i in to_print:
      msg = ""
      if i.get("event_type") == "create_mark":
        subject = i.get("subject_name")
        msg += "Новая оценка -  " + i.get("new_mark_value") + ", " + str(i.get("new_mark_weight")) + "\n" + subject + " - " + i.get("control_form_name") + "\n"
        response2 = requests.get(mark_url,  headers = {
          'Auth-Token': token
        }).json()
        for j in response2:
          if (j.get("subject_name") == subject):
            msg += "Средний балл равен " + j.get("periods")[0].get("avg_five")
        msg += "\n" + i.get("datetime").split(".")[0]
        bot.send_message(id_t, msg)
    with open('Cache.json', 'w') as outfile:
      json.dump(cache, outfile)
    has_new_info = False
  time.sleep(30)