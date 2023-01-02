#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import time
from datetime import datetime, timedelta

if __name__ == '__main__':
    print('Starting cleanup server')
    root_path = os.getcwd()
    cache_path = os.path.join(root_path, 'cache')
    captured_frames_path = os.path.join(cache_path, 'captured_frames')
    os.makedirs(captured_frames_path, exist_ok=True)
    
    keep_records_for = 2 # day
    date_threshold = (datetime.now() - timedelta(hours=24)).timestamp()

    while True:
        try:
            captured_frames_labels = os.listdir(captured_frames_path)
            for label in captured_frames_labels:
                captured_frames_label_path = os.path.join(captured_frames_path, label)
                captured_frames_list = os.listdir(captured_frames_label_path)

                for captured_frames_fn in captured_frames_list:
                    if float(captured_frames_fn.replace('.jpg','')) < date_threshold:
                        captured_frames_list_path = os.path.join(captured_frames_label_path, captured_frames_fn)
                        os.remove(captured_frames_list_path)

            time.sleep(15)

        except KeyboardInterrupt:
            print(f'Stopping cleanup server')
            pass


# In[ ]:





# In[ ]:




