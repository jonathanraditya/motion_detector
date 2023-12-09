#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import shutil
import os
import time
from global_modules import GlobalOperations
from datetime import datetime, timedelta
go = GlobalOperations()

if __name__ == '__main__':
    print(f'{go.datetime_now()} Starting Google Drive cleanup server')
    # root_path = os.getcwd()
    # cache_path = os.path.join(root_path, 'cache')
    # captured_frames_path = os.path.join(cache_path, 'captured_frames')
    # os.makedirs(captured_frames_path, exist_ok=True)

    # source_path = go.config['CCTV_PROOF_PATH'] # G:\My Drive\cctv_proof
    source_path = 'G:\\My Drive\\cctv_proof'
    os.makedirs(source_path, exist_ok=True)

    # target_path = go.config['CCTV_LONG_STORAGE_PATH'] # D:\cctv_proof
    target_path = 'D:\\cctv_proof'
    os.makedirs(target_path, exist_ok=True)
    
    keep_records_for = 120 # day(s)

    try:
        while True:
            cleanup_counter = 0
            # beginning_storage = go.free_storage(root_path)
            date_threshold = (datetime.now() - timedelta(hours=keep_records_for * 24)).timestamp()
            # captured_frames_label = os.listdir(captured_frames_path)
            source_files = os.listdir(source_path)

            for source_file in source_files:
                if float(source_file[:10]) < date_threshold:
                    source_file_path = os.path.join(source_path, source_file)
                    target_file_path = os.path.join(target_path, source_file)

                    try:
                        shutil.copy(source_file_path, target_file_path)
                        os.remove(source_file_path)
                        print(f'{go.datetime_now()} Copying: {target_file_path}')
                    except FileNotFoundError:
                        print(f'{go.datetime_now()} Failed file not found: {target_file_path}')
                    except OSError:
                        print(f'{go.datetime_now()} Copy or remove file has failed. Leaving the condition as it is: {target_file_path}')
                        

                cleanup_counter += 1
            print(f'{go.datetime_now()} Google Drive cleanup finished. {cleanup_counter} records cleaned.')

            for _ in range(60*60):
                # 1 hour
                time.sleep(1)

    except KeyboardInterrupt:
        print(f'{go.datetime_now()} Google Drive cleanup server stopped.')
        pass

            
                    
                    
            
    #         for label in captured_frames_label:
    #             captured_frames_label_path = os.path.join(captured_frames_path, label)
    #             captured_frames_list = os.listdir(captured_frames_label_path)

    #             for captured_frames_fn in captured_frames_list:
    #                 if float(captured_frames_fn.replace('.jpg','')) < date_threshold:
    #                     captured_frames_list_path = os.path.join(captured_frames_label_path, captured_frames_fn)
    #                     os.remove(captured_frames_list_path)
    #                     cleanup_counter += 1

    #         ending_storage = go.free_storage(root_path)
    #         print(f'{go.datetime_now()} Cleanup finished. {cleanup_counter} records cleaned.')
    #         for _ in range(60*60):
    #             # 1 hour
    #             time.sleep(1) 

    # except KeyboardInterrupt:
    #     print(f'{go.datetime_now()} Cleanup server stopped.')
    #     pass


# In[2]:


# import os
# import time
# from global_modules import GlobalOperations
# from datetime import datetime, timedelta
# go = GlobalOperations()


# In[1]:


# a = '1689831016.0.jpg_garden_6b20804c7e7a6dd2766b36fbb7e8567ae9ff20ba8e9141c2806f897f524b65c8.jpg'
# a[:10]


# In[3]:


# keep_records_for = 2 # hours
# dt = (datetime.now() - timedelta(hours=keep_records_for * 24)).timestamp()


# In[4]:


# dt


# In[ ]:




