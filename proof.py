#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import shutil
import time
from global_modules import GlobalOperations
go = GlobalOperations()

if __name__ == '__main__':
    print(f'{go.datetime_now()} Starting proof storing server')
    root_path = os.getcwd()
    cache_path = os.path.join(root_path, 'cache')
    proof_path = os.path.join(cache_path, 'proof')
    os.makedirs(proof_path, exist_ok=True)
    proof_list = os.listdir(proof_path)

    captured_frames_path = os.path.join(cache_path, 'captured_frames')

    cctv_proof_path = go.config['CCTV_PROOF_PATH']
    os.makedirs(cctv_proof_path, exist_ok=True)

    try:
        while True:
            for proof_label in proof_list:
                proof_label_path = os.path.join(proof_path, proof_label)
                proof_label_list = os.listdir(proof_label_path)
                for proof_fn in proof_label_list:
                    proof_label_list_path = os.path.join(proof_label_path, proof_fn)
                    with open(proof_label_list_path, 'r') as f:
                        sha256 = f.read()

                    captured_frames_label_path = os.path.join(captured_frames_path, proof_label)
                    captured_frames_img_path = os.path.join(captured_frames_label_path, proof_fn.replace('.cache','.jpg'))

                    cctv_proof_img_fn = proof_fn.replace('.cache','.jpg') + f'_{proof_label}_{sha256}.jpg'
                    cctv_proof_img_path = os.path.join(cctv_proof_path, cctv_proof_img_fn)

                    try:
                        shutil.copy(captured_frames_img_path, cctv_proof_img_path)
                        print(f'{go.datetime_now()} Copying: {cctv_proof_img_path}')
                    except FileNotFoundError:
                        print(f'{go.datetime_now()} Failed file not found: {cctv_proof_img_path}')

                    # Remove proof queue
                    os.remove(proof_label_list_path)
            time.sleep(1)
            
            
    except KeyboardInterrupt:
        print(f'{go.datetime_now()} Stopping proof storing server')
        pass


# In[2]:


# import os
# import shutil
# from global_modules import Sqlite_v2
# import pandas as pd


# In[13]:


# root_path = os.getcwd()
# cache_path = os.path.join(root_path, 'cache')
# proof_cp_path = os.path.join(cache_path, 'proof - Copy')
# proof_or_path = os.path.join(cache_path, 'proof')
# os.makedirs(proof_cp_path, exist_ok=True)
# proof_list = os.listdir(proof_cp_path)

# captured_frames_path = os.path.join(cache_path, 'captured_frames')

# cctv_proof_path = go.config['CCTV_PROOF_PATH']
# os.makedirs(cctv_proof_path, exist_ok=True)

# sqlite = Sqlite_v2()
# sqlite.set_table('notifications')
# sqlite.create_connection('./db/'+go.config['NOTIFICATIONS_DB'])

# df = pd.read_sql(f'select * from notifications', sqlite.conn)

# for proof_fn in proof_list:
#     proof_list_path = os.path.join(proof_cp_path, proof_fn)
#     with open(proof_list_path, 'r') as f:
#         sha256 = f.read()
        
#     label = df.loc[df['sha256'] == sha256]['triggered_by']
    
#     proof_dest_label_path = os.path.join(proof_or_path, label.values[0])
#     proof_dest_path = os.path.join(proof_dest_label_path, proof_fn)
    
#     shutil.copy(proof_list_path, proof_dest_path)
    
#     os.remove(proof_list_path)






# In[ ]:




