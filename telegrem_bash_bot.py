#!/usr/bin/env python3

import requests
import time
import random
import re
from threading import Timer

# Common variables
URL = 'https://api.telegram.org/bot'
TOKEN = 'your token here'
offset = 0
# Bash variables
bash_commands = ['bash', 'баш']
bash_sendto = ['-1001319536279']

def get_updates(offset):
  data = {'offset': offset, 'limit': 0, 'timeout': 0}
  try:
    request = requests.post(URL + TOKEN + '/getUpdates', data=data)
  except KeyboardInterrupt:
    exit(0)
  except:
    return False
  if not request.status_code == 200:
    return False
  elif not request.json()['ok']:
    return False
  else:
    return request.json()

def send_message(chat_id, text):
  message_data = { 'chat_id': chat_id, 'text': text }
  request = requests.post(URL + TOKEN + '/sendMessage', data=message_data)

def bashorg():
  def changer(text, change_map):
    for item in change_map.keys():
      text = text.replace(item, change_map[item])
    return text

  change_map = { '<br>': '\n', '&quot;': '"',
                 '&lt;': '<', '&gt;': '>',
                 '<br />': '\n' }
  url = 'https://bash.im/random'
  request = requests.get(url)
  result = request.text
  pattern = re.compile('<div class="text">(.*)</div>')
  quotes = pattern.findall(result)
  return changer(random.choice(quotes), change_map)

def bashorg_timejob():
  Timer(21600, bashorg_timejob).start ()
  for recipient in bash_sendto:
    send_message(recipient, bashorg())

bashorg_timejob()

while True:
  updates_json = get_updates(offset)
  if updates_json:
    updates = updates_json['result']
    for update in updates:
      print(update)
      offset = update['update_id'] + 1
      if 'message' not in update or 'text' not in update['message']:
        continue
      sender_id = update['message']['chat']['id']
      type = update['message']['chat']['type']
      if type == 'private':
        if update['message']['text'].lower() in bash_commands:
          send_message(sender_id, bashorg())
      time.sleep(1)
