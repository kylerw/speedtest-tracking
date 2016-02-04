import os
import re
import sqlite3 as lite
import sys
import time
import logging
import config
#import plotly.plotly as py
#import plotly
#from plotly.graph_objs import *
#import pandas as pd


SPEEDTEST_CMD = config.SPEEDTEST_FILE_LOCATION 
LOG_FILE = config.LOG_FILE
DB_FILE = config.DB_FILE 

def main():
  setup_logging()
  try:
    logging.info("Starting test....")
    ping, download, upload = get_speedtest_results()
  except ValueError as err:
    logging.info("Error ----")
    logging.info(err)
  else:
    logging.info("Test successful, results: ")
    logging.info("%5.1f %5.1f %5.1f", ping, download, upload)
    db_insert(ping, download, upload)


def setup_logging():
  logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)

def db_insert(ping, download, upload):
  con = lite.connect(DB_FILE)

  with con:
    try:
      sql = 'create table if not exists data (id INTEGER PRIMARY KEY, Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, ping REAL, download REAL, upload REAL)'
      cur = con.cursor()
      cur.execute(sql)
      con.commit()
    except lite.Error as err:
      logging.info("SQLite error on table creation: ")
      logging.info(err)

    try:
      sql = 'INSERT INTO data(ping, download, upload) VALUES({0}, {1}, {2})'.format(ping, download, upload)
      '''
      sys.stdout.write(sql)
      sys.stdout.flush()
      '''
      cur.execute(sql)

      con.commit()
    except lite.Error as err:
      logging.info("SQLite error on data insert: ")
      logging.info(err)

def get_speedtest_results():
  '''
  Run test and parse results.
  Returns tuple of ping speed, download speed, and upload speed,
  or raises ValueError if unable to parse data.
  '''

  ping = download = upload = None

  with os.popen(SPEEDTEST_CMD + ' --simple') as speedtest_output:

    for line in speedtest_output:
      label, value, unit = line.split()
      if 'Ping' in label:
        p = float(value)
      elif 'Download' in label:
        d = float(value)
      elif 'Upload' in label:
        u = float(value)

  if all((p, d, u)):  # if all 3 values were parsed
    return p, d, u
  else:
    raise ValueError('TEST FAILED')


if __name__ == '__main__':
  main()








