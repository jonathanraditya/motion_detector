#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from global_modules import Sqlite, GlobalOperations
import os
import sys, getopt
import time
go = GlobalOperations()

def main(argv):
    opts, args = getopt.getopt(argv, "hl:")
    for opt, arg in opts:
        if opt == '-h':
            print('-l <label>')
            sys.exit()
        elif opt in ('-l'):
            return arg
        else:
            print(f'{go.datetime_now()} Please specify label parameter first')
            sys.exit()
            
if __name__ == '__main__':
    
    label = main(sys.argv[1:])
    # print(sys.argv[1:])
    # print(label)

    root_path = os.getcwd()
    db_path = os.path.join(root_path, 'db')
    movement_signal_db_path = os.path.join(db_path, 'movement_signal.db')
    cache_path = os.path.join(root_path, 'cache')
    movements_path = os.path.join(cache_path, 'movements')
    thresholds_path = os.path.join(movements_path, 'thresholds')
    thresholds_label_path = os.path.join(thresholds_path, label)
    os.makedirs(thresholds_label_path, exist_ok=True)
    
    # Constants
    capture_rate = 1.65 #seconds
    # 24hrs * 60mins * 60secs, a day in seconds (old value)
    # 1hr * 5mins * 60secs, a day in seconds
    data_limit = int(1 * 5 * 60 / capture_rate) 
    
    # Database initialization
    sqlite = Sqlite()
    sqlite.set_table(label)
    sqlite.create_connection(movement_signal_db_path)
    
    # Processing threshold
    try:
        while True:
            df = pd.read_sql(f'select * from {label} order by ROWID desc limit {data_limit}', sqlite.conn)
            df['value'] = df['value'].astype('int')
            threshold = df['value'].mean() + 3*df['value'].std()
            # filtered_1std = df.loc[df['value'] > (df['value'].mean() + df['value'].std())]
            # threshold = filtered_1std['value'].mean() + filtered_1std['value'].std()
            timestamp = df.iloc[0]['timestamp']

            # Store threshold
            threshold_path = os.path.join(thresholds_label_path, f'{timestamp}.cache')
            with open(threshold_path, 'w') as f:
                f.write(str(threshold))

            # Keep last 10 threshold
            threshold_value_list = os.listdir(thresholds_label_path)
            if len(threshold_value_list) > 10:

                tvl_float = [float(i.replace('.cache','')) for i in threshold_value_list]
                tvl_float.sort(reverse=False) # ascending, oldest value first

                for fn in tvl_float[:len(tvl_float) - 10]:
                    threshold_value_todelete = os.path.join(thresholds_label_path, f'{fn}.cache')
                    if os.path.isfile(threshold_value_todelete):
                        os.remove(threshold_value_todelete)

            print(f"{go.datetime_now()} movement_signal_threshold_updater.py -l {label} is waiting for new data...")
            time.sleep(60)
    
    except KeyboardInterrupt:
        print(f'{go.datetime_now()} Stopping movement signal threshold server at {label}')
        pass


# In[77]:


# import pandas as pd
# from global_modules import Sqlite
# import os
# import sys, getopt
# import time
# import numpy as np

# label = 'hallway'

# root_path = os.getcwd()
# db_path = os.path.join(root_path, 'db')
# movement_signal_db_path = os.path.join(db_path, 'movement_signal.db')

# # Constants
# capture_rate = 1.65 #seconds
# data_limit = int(24 * 60 * 60 / capture_rate) # 24hrs * 60mins * 60secs, a day in seconds

# # Database initialization
# sqlite = Sqlite()
# sqlite.set_table(label)
# sqlite.create_connection(movement_signal_db_path)

# df = pd.read_sql(f'select * from {label} order by ROWID desc limit {data_limit}', sqlite.conn)
# df['value'] = df['value'].astype('int')
# filtered_1std = df.loc[df['value'] > (df['value'].mean() + df['value'].std())]
# threshold = filtered_1std['value'].mean() + filtered_1std['value'].std()
# timestamp = df.iloc[0]['timestamp']


# In[78]:


# Q1 = np.percentile(df['value'], 25, interpolation='midpoint')
# Q2 = np.percentile(df['value'], 50, interpolation='midpoint')
# Q3 = np.percentile(df['value'], 75, interpolation='midpoint')


# In[79]:


# threshold


# In[80]:


# df['value'].median() + 1*df['value'].std()


# In[81]:


# filtered_1std


# In[ ]:





# In[ ]:





# In[ ]:




