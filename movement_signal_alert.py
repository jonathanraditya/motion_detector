#!/usr/bin/env python
# coding: utf-8

# In[11]:


import os
from datetime import datetime
import sys, getopt
import time
import psutil
from global_modules import GlobalOperations
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
    print(f'{go.datetime_now()} movement_signal_alert.py -l "{label}" Starting movement signal alert server at {label}')
    
    try:
        while True:
            root_path = os.getcwd()
            cache_path = os.path.join(root_path, 'cache')
            movements_path = os.path.join(cache_path, 'movements')
            thresholds_path = os.path.join(movements_path, 'thresholds')
            thresholds_label_path = os.path.join(thresholds_path, label)
            os.makedirs(thresholds_label_path, exist_ok=True)

            # Get last threshold
            thresholds_list = os.listdir(thresholds_label_path)
            if thresholds_list == []:
                print(f'{go.datetime_now()} movement_signal_alert.py -l "{label}" Waiting for threshold data...')
                time.sleep(10)
                continue
            thl_float = [float(i.replace('.cache','')) for i in thresholds_list]
            thl_float.sort(reverse=True) # Descending, newest value first
            threshold_still_reading = True
            while threshold_still_reading:
                for threshold_fn in thl_float:
                    try:
                        threshold_path = os.path.join(thresholds_label_path, f'{threshold_fn}.cache')
                        with open(threshold_path, 'r') as f:
                            threshold = float(f.read())
                            threshold_still_reading = False
                            break
                    except ValueError:
                        print(f'{go.datetime_now()} movement_signal_alert.py -l "{label}" Threshold reading failed. Trying another threshold cache. Last path: {threshold_path}')
                        time.sleep(0.1)
                if threshold_still_reading:
                    print(f'{go.datetime_now()} movement_signal_alert.py -l "{label}" All threshold reading attempt failed. Wating for more threshold data...')
                    time.sleep(10)
                    continue

            readings_path = os.path.join(movements_path, 'readings')
            readings_label_path = os.path.join(readings_path, label)
            os.makedirs(readings_label_path, exist_ok=True)

            readings_list = os.listdir(readings_label_path)
            if readings_list == []:
                time.sleep(0.5)
                continue
            readings_float = [float(i.replace('.cache','')) for i in readings_list]
            readings_float.sort(reverse=False) # Ascending, oldest value first
            readings_list_ff = [str(i) + '.cache' for i in readings_float]

            # Store to notification channel
            notifications_path = os.path.join(cache_path, 'notifications')
            notifications_label_path = os.path.join(notifications_path, label)
            os.makedirs(notifications_label_path, exist_ok=True)

            for reading_fn in readings_list_ff:
                reading_path = os.path.join(readings_label_path, reading_fn)
                try:
                    with open(reading_path, 'r') as f:
                        reading = int(f.read())
                except ValueError:
                    print(f'{go.datetime_now()} movement_signal_alert.py -l "{label}" Value error. Assume 0 reading value.')
                    reading = 0
                    with open(reading_path, 'w') as f:
                        f.write(str(0))

                if reading > threshold:
                    notifications_path = os.path.join(notifications_label_path, reading_fn)
                    data_time = datetime.fromtimestamp(float(reading_fn.replace('.cache','')))
                    data_time = data_time.strftime('%H:%M:%S')
                    storage = psutil.disk_usage(root_path)
                    content = f'''{data_time} {label} val:{reading} threshold:{int(threshold)} free_storage:{int(storage.free / (2**30))}GB'''
                    print(content)
                    with open(notifications_path, 'w') as f:
                        f.write(content)

                # Delete reading cache that has been processed
                try:
                    os.remove(reading_path)
                except PermissionError:
                    print(f'{go.datetime_now()} movement_signal_alert.py -l "{label}" Failed to remove {reading_path}')
                    pass
                
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(f'{go.datetime_now()} Stopping movement signal alert server at {label}')
        pass

