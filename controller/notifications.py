#!/usr/bin/env python
# coding: utf-8

# In[37]:


import os
import requests
import time
import random
from global_modules import GlobalOperations, Sqlite_v2
from html import escape
import shutil
            
if __name__ == '__main__':   
    try:
        while True:
            TOKEN = '2002016705:AAGcXBOdx_OAj5LSVxu1LAjVO_xIih8bdfA'
            # Ito, chita, ibu
            CHAT_IDS = ['1217210026','1293826547','5580614403']
            # CHAT_IDS = ['@jonathanraditya']


            root_path = os.getcwd()
            cache_path = os.path.join(root_path, 'cache')
            notifications_path = os.path.join(cache_path, 'notifications')
            os.makedirs(notifications_path, exist_ok=True)
            notifications_label_list = os.listdir(notifications_path)

            captured_frames_path = os.path.join(cache_path, 'captured_frames')
            
            deception_path = os.path.join(cache_path, 'deception')
            os.makedirs(deception_path, exist_ok=True)
            
            db_path = os.path.join(root_path, 'db')
            notifications_db = os.path.join(db_path, 'notifications.db')
            sqlite = Sqlite_v2()
            sqlite.set_table('notifications')
            sqlite.create_connection(notifications_db)
            notifications_db_cols = ['timestamp','sha256','flag','triggered_by']
            notifications_db_dtypes = ['text','text','text','text']           

            proof_path = os.path.join(cache_path, 'proof')
            os.makedirs(proof_path, exist_ok=True)

            for notification_label in notifications_label_list:
                notifications_label_path = os.path.join(notifications_path, notification_label)
                os.makedirs(notifications_label_path, exist_ok=True)

                notifications_list = os.listdir(notifications_label_path)
                nl_float = [float(i.replace('.cache','')) for i in notifications_list]
                nl_float.sort(reverse=False) # Ascending order, oldest first'
                notifications_list_ff = [str(i) + '.cache' for i in nl_float]

                for notification_fn in notifications_list_ff:
                    go = GlobalOperations()
                    sha256 = go.gethash(str(random.random()))

                    notification_path = os.path.join(notifications_label_path, notification_fn)
                    with open(notification_path, 'r') as f:
                        caption = f.read()

                    captured_frames_label_path = os.path.join(captured_frames_path, notification_label)
                    captured_frames_img_path = os.path.join(captured_frames_label_path, notification_fn.replace('.cache','.jpg'))
                    captured_frames_img_path_cache = os.path.join(root_path, f'a{sha256}.jpg')

                    try:
                        shutil.copy(captured_frames_img_path, captured_frames_img_path_cache)
                    except FileNotFoundError:
                        shutil.copy(os.path.join(root_path, 'image_not_found.jpg'), captured_frames_img_path_cache)
                    captured_frames_img = open(captured_frames_img_path_cache, 'rb')
                    files = {'photo': captured_frames_img}

                    caption = escape(f'{caption} id:{sha256[:3]}-{sha256[-3:]}')
                    print(caption)

                    # Send Messages
                    for CHAT_ID in CHAT_IDS:
                        sent = False
                        while not sent:
                            try:
                                captured_frames_img = open(captured_frames_img_path_cache, 'rb')
                                files = {'photo': captured_frames_img}
                                send_message = f'https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={CHAT_ID}&caption={caption}'
                                response = requests.get(send_message, files=files)
                                # print(response.content)
                                # print(f'Sent to: {CHAT_ID}')
                                captured_frames_img.close()
                                sent = True
                            except requests.exceptions.RequestException as e:
                                print(f'{e} Trying to send notification. Wait for 5 seconds.')
                                time.sleep(5)
                        
                    # Store to proofing server
                    proof_label_path = os.path.join(proof_path, notification_label)
                    os.makedirs(proof_label_path, exist_ok=True)
                    proof_path_fn =  os.path.join(proof_label_path, notification_fn)
                    with open(proof_path_fn, 'w') as f:
                        f.write(sha256)
                        
                    # Store to deception server
                    deception_path_fn = os.path.join(deception_path, notification_fn) 
                    with open(deception_path_fn, 'w') as f:
                        f.write('0')
                        
                    # Store to db
                    notifications_db_values = [notification_fn.replace('.cache',''), sha256, '0', notification_label]
                    sqlite.insert_value(notifications_db_cols, notifications_db_values, notifications_db_dtypes)
                        
                    # Clear cache
                    try:
                        os.remove(captured_frames_img_path_cache)
                    except PermissionError:
                        print(f'Failed to remove {captured_frames_img_path_cache}')
                    os.remove(notification_path)
                    
            #         break
            #     break
            time.sleep(0.5)
            # break
                        
    except KeyboardInterrupt:
        print(f'Stopping notifications server')
        pass


# In[ ]:




