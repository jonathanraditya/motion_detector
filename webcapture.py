#!/usr/bin/env python
# coding: utf-8

# In[17]:


import os
import time
import sys, getopt
from tqdm import trange
from global_modules import GlobalOperations

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import WebDriverException

go = GlobalOperations()

capture_interval = 0.7 #second(s)
live_for = 240 #second(s), server lived for
capture_per_session = int(live_for / capture_interval)
wait_timeout = 20 #second(s)
browser_ttl = 50 # browser time to live. Quit and restart browser after n number of sessions.

options, service, driver, wait = None, None, None, None

root_path = os.getcwd()
browser_bin_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'
bin_path = os.path.join(root_path, 'bin')
driver_bin_path = os.path.join(bin_path, 'geckodriver.exe')

def main(argv):
    opts, args = getopt.getopt(argv, "hu:")
    for opt, arg in opts:
        if opt == '-h':
            print('-u <urlhost>')
            sys.exit()
        elif opt in ('-u'):
            return arg
        else:
            print(f'{go.datetime_now()} Please specify urlhost parameter first')
            sys.exit()
        
# Serve forever
if __name__ == "__main__":
    urlhost = main(sys.argv[1:])
    print(f'{go.datetime_now()} Starting Hikvision capture server at {urlhost}')
    
    try:
        print(f'{go.datetime_now()} Start new instance')
        while True:
            try:
                while True:
                    # Make sure to clean previous instance
                    go.delete(options, service, driver, wait)

                    options = Options()
                    options.binary_location = browser_bin_path
                    service = Service(executable_path=driver_bin_path, log_path=os.devnull)
                    driver = webdriver.Firefox(service=service, options=options)
                    wait = WebDriverWait(driver, wait_timeout)
                    
                    print(f'{go.datetime_now()} Opening new browser window. Browser time to live: {browser_ttl}')
                    print(f'{go.datetime_now()} Connecting to: http://{urlhost}/')
                    
                    for b in range(browser_ttl):
                        try:
                            driver.get(f"http://{urlhost}/")
                            print(f'{go.datetime_now()} {b+1}/{browser_ttl} browser cycle.')
                            # Relogin in every start of the capture session                       
                            # Login page
                            wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/table/tbody/tr/td[2]/div/div[5]/button')))
                            driver.find_element('id', 'username').send_keys(go.config['CCTV_GLOBAL_USERNAME_URLENCODED'])
                            driver.find_element('id', 'password').send_keys(go.config['CCTV_GLOBAL_PASSWORD'])
                            driver.find_element('xpath', '/html/body/div[2]/table/tbody/tr/td[2]/div/div[5]/button').click()    
                            print(f'{go.datetime_now()} Login success at {urlhost}')
    
                            # Capture button
                            print(f'{go.datetime_now()} Capturing frames at {urlhost}...')
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
                            print(f'{go.datetime_now()} End of capture session. Reloggin...')
                        except TimeoutException:
                            print(f'{go.datetime_now()} webcapture.py -u "{urlhost}" Capture request timeout. Wait for {wait_timeout}s.')
                            time.sleep(wait_timeout)
                        except (ElementClickInterceptedException, WebDriverException):
                            print(f'{go.datetime_now()} webcapture.py -u "{urlhost}" Capture failed. ElementClickInterceptedException or WebDriverException. Wait for {wait_timeout}s and retrying from login page.')

                    
                    # Closing & relaunching driver every `browser_ttl` times
                    print(f'{go.datetime_now()} End of browser time to live. Closing browser window and launch again.')
            except TimeoutException:
                print(f'{go.datetime_now()} webcapture.py -u "{urlhost}" Request timeout. Wait for {wait_timeout}s.')
                time.sleep(wait_timeout)
            except (ElementClickInterceptedException, WebDriverException):
                print(f'{go.datetime_now()} webcapture.py -u "{urlhost}" ElementClickInterceptedException or WebDriverException. Wait for {wait_timeout}s and retrying from login page.')

    except KeyboardInterrupt:
        print(f'{go.datetime_now()} Stopping Hikvision capture server at {urlhost}')
        pass


# In[ ]:




