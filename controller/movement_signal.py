#!/usr/bin/env python
# coding: utf-8

# `env:cv2`

# In[2]:


import cv2, time
import os
import numpy as np
import h5py
import sys, getopt
from global_modules import Sqlite_v2

def main(argv):
    opts, args = getopt.getopt(argv, "hl:")
    for opt, arg in opts:
        if opt == '-h':
            print('-l <label>')
            sys.exit()
        elif opt in ('-l'):
            return arg
        else:
            print('Please specify label parameter first')
            sys.exit()
            
            
if __name__ == '__main__':
    
    label = main(sys.argv[1:])
    print(f'Starting movement signal server at {label}')
    
    root_path = os.getcwd()
    cache_path = os.path.join(root_path, 'cache')
    captured_frames_path = os.path.join(cache_path, 'captured_frames')
    source_path = os.path.join(captured_frames_path, label)
    

    # Get current progress
    movements_path = os.path.join(cache_path, 'movements')
    average_value_path = os.path.join(movements_path, 'average_value')
    average_value_label_path = os.path.join(average_value_path, label)
    os.makedirs(average_value_label_path)
    average_value_list = os.listdir(average_value_label_path)
    average_value_latest = average_value_list[-1] if average_value_list != [] else False

    # Readings cache
    readings_path = os.path.join(movements_path, 'readings')
    readings_label_path = os.path.join(readings_path, label)
    os.makedirs(readings_label_path)

    # Readings db
    db_path = os.path.join(root_path, 'db')
    readings_db = os.path.join(db_path, 'movement_signal.db')
    sqlite = Sqlite_v2()
    sqlite.set_table('label')
    sqlite.create_connection(readings_db)
    readings_db_cols = ['timestamp','value']
    readings_db_dtypes = ['float','int']

    try:
        while True:
            # Get updated source list
            source_list = os.listdir(source_path)
            
            # Get updated progress
            hotstart = True
            average_value_list = os.listdir(average_value_label_path)
            average_value_latest = average_value_list[-1] if average_value_list != [] else False
            
            for filename in source_list:
                if average_value_latest and hotstart:
                    if (filename.replace('.jpg','') != average_value_latest.replace('.hdf5','')):
                        continue
                    elif (filename.replace('.jpg','') != average_value_latest.replace('.hdf5','')):
                        average_value_latest_path = os.path.join(average_value_label_path, average_value_latest)
                        with h5py.File(average_value_latest_path, 'r') as f:
                            average_value = f[()]['average_value']
                        hotstart = False
                elif average_value_latest == []:
                    average_value = np.float32(img_blurred)

                moving_avg_path = os.path.join(source_path, filename)
                img = cv2.imread(moving_avg_path, cv2.IMREAD_GRAYSCALE)
                img_blurred = cv2.GaussianBlur(img, (35,35),0)

                cv2.accumulateWeighted(img_blurred, average_value, 0.25)

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
                readings_db_values = [float(filename.replace('.jpg','')), int(high_value_count)]
                sqlite.insert_value(readings_db_cols, readings_db_values, readings_db_dtypes)

                # Create checkpoint of image average_value every x times. Store with timestamp
                # Restart from that point.
                average_value_checkpoint = os.path.join(average_value_label_path, filename.replace('.jpg','.hdf5'))
                with h5py.File(average_value_checkpoint, 'w') as f:
                    f.create_dataset('average_value', data=average_value, compression='gzip', compression_opts=9)

                # Keep last 10 checkpoint
                average_value_list = os.listdir(average_value_label_path)
                if len(average_value_list) > 10:
                    for fn in average_value_list[:len(average_value_list) - 10]:
                        average_value_todelete = os.path.join(average_value_label_path, fn)
                        if os.path.isfile(average_value_todelete):
                            os.remove(average_value_todelete)
                            
            time.sleep(2)
    
    except KeyboardInterrupt:
        print(f'Stopping movement signal server at {label}')
        pass


# In[ ]:





# In[ ]:





# In[ ]:




