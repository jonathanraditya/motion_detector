#!/usr/bin/env python
# coding: utf-8

# In[17]:


import os
import time
import sys, getopt
from tqdm import trange

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
# import selenium.common.exceptions.WebDriverException

capture_interval = 1 #second(s)
live_for = 240 #second(s), server lived for
capture_per_session = int(live_for / capture_interval)
wait_timeout = 20 #second(s)

root_path = os.getcwd()
browser_bin_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'
bin_path = os.path.join(root_path, 'bin')
driver_bin_path = os.path.join(bin_path, 'geckodriver.exe')

options = Options()
options.binary_location = browser_bin_path
service = Service(driver_bin_path)

def main(argv):
    opts, args = getopt.getopt(argv, "hu:")
    for opt, arg in opts:
        if opt == '-h':
            print('-u <urlhost>')
            sys.exit()
        elif opt in ('-u'):
            return arg
        else:
            print('Please specify urlhost parameter first')
            sys.exit()
            

# Serve forever
if __name__ == "__main__":
    urlhost = main(sys.argv[1:])
    print(f'Starting Hikvision capture server at {urlhost}')
    
    try:
        print('Start new instance')
        with webdriver.Firefox(service=service, options=options) as driver:

            wait = WebDriverWait(driver, wait_timeout)
            driver.get(f"http://{urlhost}/")

            # Relogin every start of capture session
            while True:
                # Login page
                wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/table/tbody/tr/td[2]/div/div[5]/button')))
                driver.find_element('id', 'username').send_keys('admin')
                driver.find_element('id', 'password').send_keys('Valerian@live1')
                driver.find_element('xpath', '/html/body/div[2]/table/tbody/tr/td[2]/div/div[5]/button').click()    
                print(f'Login success at {urlhost}')

                # Capture button
                print(f'Capturing frames at {urlhost}...')
                wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div[2]/div/div[2]/span/button[3]')))
                for _ in trange(capture_per_session):
                    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div[2]/div/div[2]/span/button[3]')))
                    driver.find_element('xpath', '/html/body/div[4]/div[2]/div/div[2]/span/button[3]').click()
                    time.sleep(capture_interval)

                # Logout session
                # Logout button on main frame
                wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[2]/div[5]')))
                driver.find_element('xpath', '/html/body/div[2]/div/div[2]/div[5]').click()
                # Popup confirmation
                wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/table/tbody/tr[2]/td[2]/div/table/tbody/tr[3]/td/div/button[1]')))
                driver.find_element('xpath', '/html/body/div[1]/div/table/tbody/tr[2]/td[2]/div/table/tbody/tr[3]/td/div/button[1]').click()
                print('End of capture session. Reloggin...')

    except KeyboardInterrupt:
        print(f'Stopping Hikvision capture server at {urlhost}')
        pass


# In[18]:


os.getlogin()


# In[ ]:




