import os
import re
import sqlite3 as lite
import sys
import time
import logging
import config
import plotly.plotly as py
import plotly
from plotly.graph_objs import *
import pandas as pd


SPEEDTEST_CMD = config.SPEEDTEST_FILE_LOCATION 
LOG_FILE = config.LOG_FILE
DB_FILE = config.DB_FILE 
PLOTLY_USER = config.PLOTLY_USER
PLOTLY_API = config.PLOTLY_API
PLOTLY_NAME = config.PLOTLY_NAME
PLOTLY_PUBLIC = config.PLOTLY_PUBLIC

def main():
  setup_logging()
  try:
    logging.info("Starting test....")
    #ping, download, upload = get_speedtest_results()
  except ValueError as err:
    logging.info("Error ----")
    logging.info(err)
  else:
    logging.info("Test successful, results: ")
    #logging.info("%5.1f %5.1f %5.1f", ping, download, upload)
    #db_insert(ping, download, upload)
    plotData()

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
      cur.execute(sql)

      con.commit()
    except lite.Error as err:
      logging.info("SQLite error on data insert: ")
      logging.info(err)


def plotData():
  con = lite.connect(DB_FILE)
  
  with con:
    cur = con.cursor()
    sql = "SELECT id, ping, download, upload, datetime(Timestamp, 'localtime') FROM data" 
    cur.execute(sql)
    rows = cur.fetchall()

  df = pd.DataFrame( [[ij for ij in i] for i in rows] )
  df.rename(columns={0: 'id', 1: 'Ping', 2: 'Download', 3: 'Upload', 4:'Date'}, inplace=True);
  df = df.sort(['Date'], ascending=[1]);

  trace1 = Scatter(
     x=df['Date'],
     y=df['Download'],
     name='Download',
  )
  trace2 = Scatter(
    x=df['Date'],
    y=df['Upload'],
    name='Upload',
  )
  trace3 = Scatter(
    x=df['Date'],
    y=df['Ping'],
    name='Ping',
    yaxis='y2'
  )
  layout = Layout(
    title=PLOTLY_NAME,
    xaxis=XAxis(
        title='Date', 
        autorange=True 
    ),
    yaxis=YAxis(
        title='Speed (Mbps)',
        range=[0,150],
        type='linear',
        autorange=False,
        fixedrange=False,
        ticksuffix=' (Mbps)'
    ),
    yaxis2=YAxis(
        title='Ping Time (ms)',
        range=[0,100],
        overlaying='y',
        side='right',
        type='linear',
        autorange=False,
        ticksuffix=' (ms)'
    ),
  )

  py.sign_in(PLOTLY_USER, PLOTLY_API)
  data = Data([trace1,trace2,trace3])
  fig = Figure(data=data, layout=layout)
  py.plot(fig, filename=PLOTLY_NAME, world_readable=PLOTLY_PUBLIC)




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








