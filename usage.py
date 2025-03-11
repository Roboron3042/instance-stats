#!/usr/bin/python3
from mastodon import Mastodon
import requests
import config
import json
import os
import sys
from datetime import datetime
import psutil
from psutil._common import bytes2human
import math

client = Mastodon(
  access_token=config.access_token,
  api_base_url=config.toot_instance
)
text_usage = config.text_usage

time = datetime.utcnow().strftime("%Y-%m-%d")

ram = psutil.virtual_memory()[2]
cpu = psutil.cpu_percent(3600)
#cpu = psutil.cpu_percent(3)
disk1 = psutil.disk_usage('/')
#disk1_use = float(bytes2human(disk1.used).rstrip('GT'))
disk1_use = math.trunc( disk1.used / pow(1024,3) )
disk1_percent = disk1.percent
disk2 = psutil.disk_usage('/mnt/mastodon')
#disk2_use = float(bytes2human(disk2.used / 1024).rstrip('GT'))
disk2_use = math.trunc( disk2.used / pow(1024,3) )
disk2_percent = disk2.percent

f = open('db_usage.json', 'r')
db = json.loads(f.read())
f.close()

cpu_change = '%+-f' % (cpu - db["cpu"])
ram_change = '%+-f' % (ram - db["ram"])
disk1_use_change = '%+-f' % (disk1_use - db["disk1_use"])
disk2_use_change = '%+-f' % (disk2_use - db["disk2_use"])

text_usage = text_usage.replace("%%timestamp%%", time)
text_usage = text_usage.replace("%%cpu%%", f'{cpu}% ({cpu_change[:5]}%)')
text_usage = text_usage.replace("%%ram%%", f'{ram}% ({ram_change[:5]}%)')
text_usage = text_usage.replace("%%disk1%%", f'{disk1_use}GB ({disk1_use_change[:5]})')
text_usage = text_usage.replace("%%disk1_percent%%", f' ({disk1_percent}%)')
text_usage = text_usage.replace("%%disk2%%", f'{disk2_use}GB ({disk2_use_change[:5]})')
text_usage = text_usage.replace("%%disk2_percent%%", f' ({disk2_percent}%)')


db={'ram':ram,'cpu':cpu,'disk1_use':disk1_use,'disk2_use':disk2_use}
db = json.dumps(db)

f = open('db_usage.json', 'w')
f.write(db)
f.close()

dryrun = False
try:
  if sys.argv[1] == "--dry-run":
    dryrun = True
except:
  pass

if not dryrun:
  print(text_usage)
  client.status_post(text_usage, visibility="unlisted")
else:
  print(text_usage)
