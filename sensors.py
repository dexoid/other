#!/usr/bin/env python3

import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP085
import re
import os
import socket

# Sensors
sensors = ({ 'id': 1, 'name': 'outdoor', 'type': 'DHT', 'subtype': 22, 'pin': 5 },
           { 'id': 2, 'name': 'pressure', 'type': 'BMP', 'subtype': 85, 'pin': None },
           { 'id': 3, 'name': 'indoor', 'type': 'DHT', 'subtype': 11, 'pin': 4 }
          )

# File Report
report = '/tmp/sensors'

# Narodmon variables
mac = 'B827EB5AC2A3'
narodmon_ids = (1, 2)
narodmon_data = '#{0}\n'.format(mac)
narodmon_id = 1
narodmon_server = 'narodmon.ru'
narodmon_port = 8283

def narodmon_prepare_data(id, type, value):
  global narodmon_data
  global narodmon_id
  if id in narodmon_ids:
    if type == 'DHT':
      for element in reversed(value):
        form_data = '#' + mac + '0' + str(narodmon_id)  + '#' + str(element) + '\n' 
        narodmon_data = narodmon_data + form_data
        narodmon_id += 1
    elif type == 'BMP':
      form_data = '#' + mac + '0' + str(narodmon_id)  + '#' + str(value) + '\n'
      narodmon_data = narodmon_data + form_data
      narodmon_id += 1

def narodmon_send_data():
  sock = socket.socket()
  try:
    sock.connect((narodmon_server, narodmon_port))
    sock.send((narodmon_data + '##').encode())
    data = sock.recv(1024)
    sock.close()
  except socket.error:
    print('Error sending data to narodmon.')

def dht_get_data(dht_type, pin):
  try:
    data = [round(x, 1) for x in Adafruit_DHT.read_retry(dht_type, pin)]
  except TypeError:
    print('Error! Result is not float type.')
    return [None, None]
  return data

def bmp_get_data():
  sensor = BMP085.BMP085()
  data = round(sensor.read_sealevel_pressure()*0.00750062,2)
  return data

def write_to_report(name, value, file):
  if not os.path.isfile(file):
    open(file, 'a').close()
  data = open(file).read()
  pattern = name + ':.*'
  if re.search(pattern, data):
    f = open(file, 'w')
    f.write(re.sub(pattern, value, data))
  else:
    f = open(file, 'a')
    f.write(value + '\n')  
  f.close()

for sensor in sensors:
  if sensor['type'] == 'DHT':
    value = dht_get_data(sensor['subtype'], sensor['pin'])
    formatvalue = "{0}:{1}:{2}".format(sensor['name'], value[1], value[0])
  elif sensor['type'] == 'BMP':
    value = bmp_get_data()
    formatvalue = "{0}:{1}".format(sensor['name'], value)
  if str(None) not in str(value):
    write_to_report(sensor['name'], formatvalue, report)
    narodmon_prepare_data(sensor['id'], sensor['type'], value)

narodmon_send_data()

