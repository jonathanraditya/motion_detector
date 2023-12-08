#!/usr/bin/env python
# coding: utf-8

# Use `env:ipykernel` or `(base)`.

# In[9]:


import os
import shutil
from datetime import datetime
import time
from global_modules import GlobalOperations
go = GlobalOperations()

origin_root = os.path.join(f'C:\\Users\\{os.getlogin()}\\Web\\CaptureFiles')
print(f'Listening at: {origin_root}')
root_path = os.getcwd()
cache_path = os.path.join(root_path, 'cache')
captured_frames_path = os.path.join(cache_path, 'captured_frames')
os.makedirs(captured_frames_path, exist_ok=True)
print(f'Target directory: {captured_frames_path}')

def main(origin_root, captured_frames_path):
    routers = {go.config['CCTV_1_NAME']:go.config['CCTV_1_IP'],
           go.config['CCTV_2_NAME']:go.config['CCTV_2_IP'],
           go.config['CCTV_3_NAME']:go.config['CCTV_3_IP']}
    routers_inversed = {v:k for k,v in routers.items()}
    
    origin_main_folders = os.listdir(origin_root)

    # parse contents in the folder & sub-folder(s)
    for origin_main_folder in origin_main_folders:
        origin_subfolder_path = os.path.join(origin_root, origin_main_folder)
        origin_subfolder_list = os.listdir(origin_subfolder_path)
        for origin_filename in origin_subfolder_list:
            origin_path = os.path.join(origin_subfolder_path, origin_filename)
            break_fn = origin_filename.replace('.jpg', '').split('_')
            label = routers_inversed[break_fn[0]]
            # convert datetime to timestamp
            timestamp = datetime.strptime(break_fn[2][:14], '%Y%m%d%H%M%S').timestamp()

            # Target directory & filename
            target_folder = os.path.join(captured_frames_path, label)
            os.makedirs(target_folder, exist_ok=True)

            target_path = os.path.join(target_folder, f'{timestamp}.jpg')

            # Move file to /cache/captured_frames, outer_fence/hallway/garden
            try:
                shutil.move(origin_path, target_path)
            except (PermissionError, FileExistsError):
                # PermissionError / FileExistsError
                # Abort moving to new location and straight remove
                print(f'Fail to move: {origin_path}')
                try:
                    os.remove(origin_path)
                except FileNotFoundError:
                    print(f'Fail to move and remove: {origin_path}')
                    pass
            
if __name__ == '__main__':
    try:
        print(f'{go.datetime_now()} capture_restructurer server is started')
        # Run infinite times.
        while True:
            main(origin_root, captured_frames_path)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(f'{go.datetime_now()} Stopping capture_restructurer server. Thank you!')


# In[ ]:




