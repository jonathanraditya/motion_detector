#!/usr/bin/env python
# coding: utf-8

# In[76]:


from dotenv import dotenv_values
config = dotenv_values('../../.env')
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import sqlite3
import os
from datetime import datetime
import pytz
import hashlib
import random
import time


# Class tree:
# -- GlobalOperations
# --- Sqlite
# ---- Vibrateserver

# In[145]:


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
        sql = f'''create table if not exists {self.table} ({col_dtypes})'''
        cur = self.conn.cursor()
        cur.execute(sql)
    
    def insert_value(self, cols, values):            
        if isinstance(self.conn, sqlite3.Connection) & isinstance(self.table, str):
            if all(isinstance(i, list) for i in [cols, values]):
                cols_all = ['datetime']
                data_placeholders = ['?']
                values_all = [f"'{str(self.datetime_now().timestamp())}'"]
                values_all = [str(self.datetime_now().timestamp())]
                col_dtypes_bind = ['datetime float']
                
                for i, col in enumerate(cols):
                    cols_all.append(col)
                    data_placeholders.append('?')
                    # values_all.append(f"'{values[i]}'")
                    values_all.append(values[i])
                    col_dtypes_bind.append(f'{col} int')
                      
                cols_insert = ','.join(cols_all)
                data_placeholder_insert = ','.join(data_placeholders)
                values_insert = ','.join(values_all)
                # print(values_insert)
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
    
class VibrateProcessor(Sqlite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_dir = os.getcwd()
        self.db = config['VIBRATION_RECORDS_DB']
        
        self.db_path = os.path.join(self.root_dir, self.db)

        self.in_sw = {
            'two_corner':['front_facing','side_facing','room_entry'],
            'two_entry':['left_sensor','right_sensor'],
            'one_perimeter':['carport_perimeter','large_gate','small_gate','garden_fence','garden_outer_perimeter'],
            'one_main':['parlor_window','main_door_upper','main_door_lower'],
            'one_hallway':['hallway_door','hallway_window']
        }
        self.out_gb = 0
        self.out_sw = {
            'two_corner':{
                'reset_trigger':0,
            },
            'two_entry':{
                'reset_trigger':0,
            },
            'one_perimeter':{
                'reset_trigger':0,
            },
            'one_main':{
                'reset_trigger':0,
            },
            'one_hallway':{
                'kitchen_lamp_switch':0,
                'outdoor_lamp_switch':0,
                'parlor_lamp_switch':0,
                'reset_trigger':0
            }
        }
        random.seed(int(config['RANDOM_SEED']))
        self.key = self.gethash(random.random())
        self.key = self.gethash(self.key)
        
        self.host = config['HOST_NODE_IP']
        self.port = int(config['HOST_NODE_PORT'])
        
        
    
class Vibrateserver(BaseHTTPRequestHandler, VibrateProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        path = urlparse(self.path).path
        vp = VibrateProcessor()
        
        # print('zero')
        if 'key' in qs.keys() and 'hwid' in qs.keys():
            # print('a')
            hwid = qs['hwid'][0]
            if qs['key'][0] == vp.key:
                # print('b')
                # Input handler
                if path == '/input':
                    # print('c')
                    if hwid in vp.in_sw.keys():
                        # print('d')
                        payload_split = qs['payload'][0].split('z')
                        if len(payload_split) == len(vp.in_sw[hwid]):
                            # print('e')
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.set_table(hwid)
                            self.create_connection(vp.db_path)
                            # print(vp.in_sw[hwid])
                            # print(payload_split)
                            # print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                            # print(hwid)
                            self.insert_value(vp.in_sw[hwid], payload_split)

                # Output handler
                elif path == '/output':
                    # print('f')
                    if hwid in vp.out_sw.keys():
                        # print('g')
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        output_csv = ','.join([str(v) for v in vp.out_sw[hwid].values()])
                        
                        self.wfile.write(bytes(output_csv, 'utf-8'))        
                        
        # print('last')
            
            
if __name__ == '__main__':
    vp = VibrateProcessor()
    webServer = HTTPServer((vp.host,vp.port), Vibrateserver)
    print(f'Server started http://{vp.host}:{vp.port}')
    
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    
    webServer.server_close()
    print('Server stopped.')


# In[153]:


# vs = Vibrateserver()
# vs.key


# In[154]:


# vs.create_connection(vs.db_path)


# In[155]:


# type(vs.conn)


# In[156]:


# isinstance(vs.conn, sqlite3.Connection)


# In[94]:


# webServer = HTTPServer((vs.host, vs.port), vs)
# print(f'Server started http://{vs.host}:{vs.port}')


# In[138]:


# vs.host


# In[ ]:


# try:
#     webServer.serve_forever()
# except KeyboardInterrupt:
#     pass


# In[149]:


# vs.path = 'http://localhost:5000/output?key=431f8a00bb579d4691b19efe332e21d8b61ff25e8a1698d81bf95a756660f3ee&hwid=one_hallway'


# In[150]:


# vs.do_GET()


# In[130]:


# urlparse(vs.path).path


# In[ ]:





# In[73]:


# from urllib.parse import urlparse, parse_qs
# url = 'localhost:8080/input?key=431f8a00bb579d4691b19efe332e21d8b61ff25e8a1698d81bf95a756660f3ee&hwid=two_corner&payload=423z982z912'
# qs = parse_qs(urlparse(url).query)
# path = urlparse(url).path


# In[151]:


# qs['hwid'][0] in ag.in_sw.keys()


# In[80]:


# ag.in_sw.keys()


# In[152]:


# 'hwid' in


# In[ ]:





# In[ ]:





# In[ ]:





# <!-- localhost:8080/input?key=431f8a00bb579d4691b19efe332e21d8b61ff25e8a1698d81bf95a756660f3ee&hwid=two_corner&payload=423z982z912 -->

# In[85]:


# f = [0,0,0]
# len(f)


# In[ ]:


# http://192.168.0.5:5000/input?key=431f8a00bb579d4691b19efe332e21d8b61ff25e8a1698d81bf95a756660f3ee&hwid=two_corner&payload=423z982z912

# http://192.168.0.5:5000/input?key=431f8a00bb579d4691b19efe332e21d8b61ff25e8a1698d81bf95a756660f3ee&hwid=two_entry&payload=423z982

# one_perimeter
# http://192.168.0.5:5000/input?key=431f8a00bb579d4691b19efe332e21d8b61ff25e8a1698d81bf95a756660f3ee&hwid=one_perimeter&payload=423z982z998z45z456


# In[ ]:


# http://192.168.0.5:5000/output?key=431f8a00bb579d4691b19efe332e21d8b61ff25e8a1698d81bf95a756660f3ee&hwid=one_hallway


# In[ ]:





# In[157]:


# a = ['front_facing', 'side_facing', 'room_entry']
# b = ['423', '982', '912']


# In[159]:


# all(isinstance(i, list) for i in [a, b])


# In[160]:


# a = ['a', 'b', 'c', 'd']
# b = ['float', 'int', 'int', 'int']
# for x, y in zip(a, b):
#     print(x, y)


# In[ ]:





# In[161]:


# a = {
#             'two_corner':{
#                 'reset_trigger':0,
#             },
#             'two_entry':{
#                 'reset_trigger':0,
#             },
#             'one_perimeter':{
#                 'reset_trigger':0,
#             },
#             'one_main':{
#                 'reset_trigger':0,
#             },
#             'one_hallway':{
#                 'kitchen_lamp_switch':0,
#                 'outdoor_lamp_switch':0,
#                 'parlor_lamp_switch':0,
#                 'reset_trigger':0
#             }
#         }


# In[172]:


# ','.join([str(v) for v in a['one_hallway'].values()])


# In[170]:


# ','.join(a['one_hallway'].values())


# In[ ]:




