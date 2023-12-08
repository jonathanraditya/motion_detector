#!/usr/bin/env python
# coding: utf-8

# Use `env:valkka` / `env:cv2`

# In[1]:


import os
os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')
import vlc
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import sqlite3
from datetime import datetime
import pytz
import hashlib
import random
import time
import pandas as pd
from global_modules import VibrateProcessor


# In[2]:


streams = {'outer_fence':{'stream_rtsp':'rtsp://admin:Valerian%40live1@192.168.0.170:554/Streaming/Channels/102/','player_obj':0},
           'garden':{'stream_rtsp':'rtsp://admin:Valerian%40live1@192.168.0.208:554/Streaming/Channels/102/','player_obj':0},
           'hallway':{'stream_rtsp':'rtsp://admin:Valerian%40live1@192.168.0.207:554/Streaming/Channels/102/','player_obj':0}}

# UPGRADE OPTIONS: Ping before connecting
# Common problems: no video showed up if no admin connection to live view

for stream_name, player_include in streams.items():
    streams[stream_name]['player_obj'] = vlc.MediaPlayer(player_include['stream_rtsp'])
    streams[stream_name]['player_obj'].play()


# In[3]:


class GlobalOperations:   
    def datetime_now(self):
        tz = pytz.timezone('Asia/Jakarta')
        return datetime.now(tz)
    
    def gethash(self, string):
        '''sha256'''
        # sanity check
        if not isinstance(string, str):
            string = str(string)            
        return hashlib.sha256(bytes(string, 'utf-8')).hexdigest()

class Sqlite(GlobalOperations):
    '''Version 2
    This version is slightly different with vibration_sensor/server version,
            especially in insert_value function.'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = None
        self.table = None
        
    def set_table(self, table):
        self.table = table
        
    def create_connection(self, db_path):
        try:
            self.conn = sqlite3.connect(db_path)
        except Error as e:
            print(f'Failed to create connection. {e}')
    
    def create_table(self, col_dtypes):
        if isinstance(self.table, str) & isinstance(col_dtypes, list):
            sql = f'''create table if not exists {self.table} ({col_dtypes})'''
            cur = self.conn.cursor()
            cur.execute(sql)
        else:
            print('Define self.table first and or recheck col_dtypes is in list type.')
            
    
    def insert_value(self, cols, values, dtypes):            
        if isinstance(self.conn, sqlite3.Connection) & isinstance(self.table, str):
            if all(isinstance(i, list) for i in [cols, values, dtypes]):
                cols_all = []
                data_placeholders = []
                values_all = []
                col_dtypes_bind = []
                
                for i, col in enumerate(cols):
                    cols_all.append(col)
                    data_placeholders.append('?')
                    values_all.append(values[i])
                    col_dtypes_bind.append(f'{col} {dtypes[i]}')
                      
                cols_insert = ','.join(cols_all)
                data_placeholder_insert = ','.join(data_placeholders)
                values_insert = ','.join(values_all)
                col_dtypes_bind_insert = ','.join(col_dtypes_bind)
                
                # Create table if not exists
                self.create_table(col_dtypes_bind_insert)
                
                sql = f'''insert into {self.table} ({cols_insert}) values ({data_placeholder_insert})'''
                # print(sql)
                cur = self.conn.cursor()
                cur.execute(sql, values_all)
                self.conn.commit()
            else:
                print('Makesure that colnames is in python list format `[...,...,...]`')
        else:
            print('Please initialize connection and table name first.')


# In[4]:


# Initiate directory, database
root_dir = os.getcwd()
db_dir = os.path.join(root_dir, 'db')
events_db = 'events.db'
events_db_path = os.path.join(db_dir, events_db)
events_table = 'events'

capture_status_api = 'is_capturing.action'
capture_status_api_path = os.path.join(root_dir, capture_status_api)

events_sq = Sqlite()
events_sq.set_table(events_table)
events_sq.create_connection(events_db_path)

# Init capture_status_api with 0
# = 0 -- no capture
# > 0 -- capture
with open(capture_status_api, 'w') as f:
    f.write('0')

# db cols
cols_init = ['no', 'sha256', 'flag', 'start_trigger', 'end_trigger']
cols_init_dtypes = ['int', 'text', 'text', 'text', 'text']
cols_insert = ['sha256', 'flag', 'start_trigger', 'end_trigger']
cols_insert_dtypes = ['text', 'text', 'text', 'text']
cols_dtypes_bind = [f'{col} {dtype}' for col, dtype in zip(cols_init, cols_init_dtypes)]

events_sq.create_table(cols_dtypes_bind)


# In[5]:


# Server rule
# Create cache file for faster reading for every in_sw (postponed)
# Use records.db to create capture_status_api status
# Read one_hallway, one_main, one_perimeter, two_corner, two_entry in the same time
vp = VibrateProcessor()
records_db = 'records.db'
records_db_path = os.path.join(db_dir, records_db)
records_db_path_rel = os.path.relpath(records_db_path, root_dir)
records_tables = list(vp.in_sw.keys())

records_sq = Sqlite()
records_sq.set_table(records_tables[1])
records_sq.create_connection(records_db_path_rel)


# In[6]:


df = pd.read_sql(f'select * from {records_sq.table}', records_sq.conn)


# In[7]:


df


# In[ ]:


'''
Rule for analysis:
- Define interval for analysis (ex: )

Active analysis:
- Define cache file:
    - start_signal (timestamp)
    - current_signal (timestamp)
    - high_value_counter (increased by +1 every non-0 value recorded)
        -> later, if this value > 
    - low_value_counter (increased by +1 every-0 value recorded)
    - last_value (rewritten with new records)
    - same_with_last_value_counter (increased by +1 if same value recorded)
    
Rule for alert:
- BASE = 15
- if for straight last 15 records are 0, and new high value recorded

Rule to end alert:
- if straight 15 records are 0
    
Rule to check if signal is valid:
- record highest value
- if highest value recorded for > 30 records -> invalid

# Pseudocode
# What not to do during warmup:
# valid/invalid categorization

# Initialization
high_value_baseline = 30
warmup_time = high_value_baseline
warmup_counter = 0
high_value = 1
high_value_counter = 0
low_value = 0
low_value_counter = 0
start_signal_timestamp = 0
current_signal_timestamp = 0
capture_counter = 0
capture_interval = 15

# Run in every new input received
# OUTPUT:
# - 
# Loop section

if current_value > high_value:
    high_value = current_value
    
if current_value == high_value:
    high_value_counter += 1
    
# Invalid value reset test
if current_value == low_value and high_value_counter > high_value_baseline:
    # 30 records straight with low value 
    # need to be achieved to bring back valid status 
    if low_value_counter < high_value_baseline:
        low_value_counter += 1
    
    # Back to valid state
    else:
        low_value_counter = 0
        high_value_counter = 0
else current_value > low_value and low_value_counter > 0:
    # Reset low_value_counter
    # (variables that used to store valid status test)
    # if high value recorded during test 
    low_value_counter = 0
    
# No capture status determination during warmup
# Important to check sensor data validity
if warmup_counter < warmup_time:
    warmup_counter += 1
            
# Capture status determination
valid = ((warmup_counter >= warmup_time) and 
            (high_value_counter <= high_value_baseline))
if current_value > 0 and valid:
    # Always reset capture_counter after 
    # fresh & valid detected vibration
    in_capture_mode = True
    capture_counter = 0
elif current_value == 0 and valid and in_capture_mode:
    if capture_counter < capture_interval:
        capture_counter += 1
    else:
        # Reset in_capture_mode
        # if no vibration detected 15s 
        # after last vibration
        in_capture_mode = False

# capture_processor.py
# Frame capture processor        
if in_capture_mode:
    capture
    record to db for analyis
    current_signal_timestamp = vp.datetime_now()


            
            
            
            
        
        
Invalid:
    
    



'''


# In[ ]:





# In[ ]:





# In[ ]:




