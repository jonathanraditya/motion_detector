#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import time
from global_modules import GlobalOperations
from datetime import datetime, timedelta
go = GlobalOperations()

if __name__ == '__main__':
    print(f'{go.datetime_now()} Starting cleanup server')
    root_path = os.getcwd()
    cache_path = os.path.join(root_path, 'cache')
    captured_frames_path = os.path.join(cache_path, 'captured_frames')
    os.makedirs(captured_frames_path, exist_ok=True)
    
    keep_records_for = 2 # day

    try:
        while True:
            cleanup_counter = 0
            beginning_storage = go.free_storage(root_path)
            date_threshold = (datetime.now() - timedelta(hours=24)).timestamp()
            captured_frames_labels = os.listdir(captured_frames_path)
            for label in captured_frames_labels:
                captured_frames_label_path = os.path.join(captured_frames_path, label)
                captured_frames_list = os.listdir(captured_frames_label_path)

                for captured_frames_fn in captured_frames_list:
                    if float(captured_frames_fn.replace('.jpg','')) < date_threshold:
                        captured_frames_list_path = os.path.join(captured_frames_label_path, captured_frames_fn)
                        os.remove(captured_frames_list_path)
                        cleanup_counter += 1

            ending_storage = go.free_storage(root_path)
            print(f'{go.datetime_now()} Cleanup finished. {cleanup_counter} records cleaned ({ending_storage - beginning_storage}GB). Free storage now: {ending_storage}GB.')
            for _ in range(60*60):
                # 1 hour
                time.sleep(1) 

    except KeyboardInterrupt:
        print(f'{go.datetime_now()} Cleanup server stopped.')
        pass


# In[ ]:





# In[ ]:




