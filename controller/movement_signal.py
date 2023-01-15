#!/usr/bin/env python
# coding: utf-8

# `env:cv2`

# In[2]:


import cv2, time
import os
import numpy as np
import h5py
import sys, getopt
from global_modules import Sqlite_v2, GlobalOperations
import sqlite3
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
    print(f'{go.datetime_now()} Starting movement signal server at {label}')
    
    # Old outer_fence value: [(21,21),0.001]
    param_sw = {'outer_fence':[(35,35),0.25],
                'garden':[(35,35),0.25],
                'hallway':[(35,35),0.25]}
    
    root_path = os.getcwd()
    cache_path = os.path.join(root_path, 'cache')
    captured_frames_path = os.path.join(cache_path, 'captured_frames')
    source_path = os.path.join(captured_frames_path, label)
    

    # Get current progress
    movements_path = os.path.join(cache_path, 'movements')
    average_value_path = os.path.join(movements_path, 'average_value')
    average_value_label_path = os.path.join(average_value_path, label)
    os.makedirs(average_value_label_path, exist_ok=True)
    average_value_list = os.listdir(average_value_label_path)
    average_value_latest = average_value_list[-1] if average_value_list != [] else False

    # Readings cache
    readings_path = os.path.join(movements_path, 'readings')
    readings_label_path = os.path.join(readings_path, label)
    os.makedirs(readings_label_path, exist_ok=True)

    # Readings db
    db_path = os.path.join(root_path, 'db')
    readings_db = os.path.join(db_path, 'movement_signal.db')
    sqlite = Sqlite_v2()
    sqlite.set_table(label)
    sqlite.create_connection(readings_db)
    readings_db_cols = ['timestamp','value']
    readings_db_dtypes = ['text','text']

    try:
        while True:
            # Get updated source list
            source_list = os.listdir(source_path)
            source_list_fl = [float(i.replace('.jpg','')) for i in source_list]
            source_list_fl.sort(reverse=False) # ascending, lowest value first
            source_list = [i for _, i in sorted(zip(source_list_fl, source_list))]
            
            # Get updated progress
            hotstart = True
            average_value_list = os.listdir(average_value_label_path)
            # average_value_latest = average_value_list[-1] if average_value_list != [] else False
            if average_value_list != []:
                avl_float = [float(i.replace('.hdf5','')) for i in average_value_list]
                avl_float.sort(reverse=True) # descending, highest value first
                average_value_latest = f'{avl_float[0]}.hdf5'
                # print(average_value_latest)
            else:
                average_value_latest = False
            
            for filename in source_list:
                if average_value_latest and hotstart:
                    if (float(filename.replace('.jpg','')) <= float(average_value_latest.replace('.hdf5',''))):
                        continue
                    else:
                        average_value_latest_path = os.path.join(average_value_label_path, average_value_latest)
                        with h5py.File(average_value_latest_path, 'r') as f:
                            average_value = f['average_value'][()]
                        hotstart = False
                elif not average_value_latest and hotstart:
                    moving_avg_path = os.path.join(source_path, filename)
                    img = cv2.imread(moving_avg_path, cv2.IMREAD_GRAYSCALE)
                    img_blurred = cv2.GaussianBlur(img, param_sw[label][0],0)
                    average_value = np.float32(img_blurred)
                    hotstart = False
                    
                if hotstart:
                    continue

                moving_avg_path = os.path.join(source_path, filename)
                img = cv2.imread(moving_avg_path, cv2.IMREAD_GRAYSCALE)
                
                try:
                    img_blurred = cv2.GaussianBlur(img, param_sw[label][0],0)
                except cv2.error as e:
                    print(e)
                    print(f'{go.datetime_now()} Removing troubled files and continue...')
                    print(moving_avg_path)
                    os.remove(moving_avg_path)
                    continue

                cv2.accumulateWeighted(img_blurred, average_value, param_sw[label][1])

                running_average = cv2.convertScaleAbs(average_value)
                diff = cv2.absdiff(running_average, img_blurred)
                thresh = cv2.threshold(diff, 100, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                resized = cv2.resize(thresh, (0,0), fx=0.2, fy=0.2)
                resized_reshaped = resized.reshape(resized.shape[0]*resized.shape[1])
                high_value_count = np.histogram(resized_reshaped, bins=5)[0][4]

                # Store value to cache (temporary)
                readings_cache_path = os.path.join(readings_label_path, filename.replace('.jpg','.cache'))
                with open(readings_cache_path, 'w') as f:
                    f.write(str(high_value_count)) 

                # Store value to db
                readings_db_values = [str(filename.replace('.jpg','')), str(high_value_count)]
                insert_in_progress = True
                while insert_in_progress:
                    try:
                        sqlite.insert_value(readings_db_cols, readings_db_values, readings_db_dtypes)
                        insert_in_progress = False
                    except sqlite3.OperationalError as e:
                        print(f'{go.datetime_now()} movement_signal.py -l {label} Insertion error. Trying to reinitiate sqlite object. {e}')
                        del sqlite
                        sqlite = Sqlite_v2()
                        sqlite.set_table(label)
                        sqlite.create_connection(readings_db)        

                # Create checkpoint of image average_value every x times. Store with timestamp
                # Restart from that point.
                average_value_checkpoint = os.path.join(average_value_label_path, filename.replace('.jpg','.hdf5'))
                with h5py.File(average_value_checkpoint, 'w') as f:
                    f.create_dataset('average_value', data=average_value, compression='gzip', compression_opts=9)

                # Keep last 10 checkpoint
                average_value_list = os.listdir(average_value_label_path)
                if len(average_value_list) > 10:
                    
                    avl_float = [float(i.replace('.hdf5','')) for i in average_value_list]
                    avl_float.sort(reverse=False) # ascending, oldest value first
                    # print(avl_float)
                        
                    for fn in avl_float[:len(avl_float) - 10]:
                        average_value_todelete = os.path.join(average_value_label_path, f'{fn}.hdf5')
                        if os.path.isfile(average_value_todelete):
                            os.remove(average_value_todelete)
                            
            print(f"{go.datetime_now()} movement_signal.py -l {label} is waiting for new data...")
            time.sleep(2)
    
    except KeyboardInterrupt:
        print(f'{go.datetime_now()} Stopping movement signal server at {label}')
        pass


# In[ ]:





# In[ ]:





# In[ ]:




