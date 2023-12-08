# Hikvision CCTV Motion Detector

A codebase to automatically capture live frames from Hikvision CCTV web interface, and using python microservices to run a live motion detector and send it to Telegram.

# Server backend controller
## `global_modules.py`
Globally used classes and functions.

## `microcontroller_server.py`
Server for vibration_server microcontroller. This would enable microcontroller to store readings (`/input`) and get output (`/output`) to the server.

## `capture.py` **(deprecated)**
A capture server implementation using VLC. This microservice is deprecated as there are stability issue arises, like:
- Frequent disconnect between server and edge device(s)
- Untolerable delay (~10s between events)
- Corrupted captured image (horizontal black/RGB lines)
- The communication between agent (VLC) and controller (python) is unreliable. It'd be better if there are: (1) sufficient documentation, (2) responsive control between service, (3) global command to end the service

I've tried many things:
- Change h265 to h264 (this is massively decrease the delay and cpu usage, as well as increase reliability)
- Maintain the WiFi signal with the range of -30dbm (very strong) to -55dbm (strong)
- Using the latest patch of the router (Tp-Link AX55)
- Lowering the resolution, from 1080p to 144p
- Using latest VLC version

but the issues still persist.

In the end, I discovered that this reliability issue is not present if the CCTV accessed directly from the native HikVision web control panel interface. They used custom engine called "LocalServiceControl" to deliver this stunning performance.

Though I haven't found any documentation regarding this system, I decided to use, control, and leverage this web interface using Selenium. The captured frames then saved into target folder.

I used saved image as a protobuf to integrate the HikVision system and my motion detector service.

## `webcapture.ipynb`
Modify `webcapture.py` by modifying the .ipynb file and exporting as "executeable script".

Run in conda terminal with `env:selenium` to create a single capture server.
Use `python webcapture.py` with `-u <urlhost>` parameter. 
Three urlhost to pass (one for each capture server):
- 192.168.0.170 -> outer_fence
- 192.168.0.207 -> hallway
- 192.168.0.208 -> garden

## `capture_restructurer.ipynb`
Move, rename, and restructure saved image produced by `webcapture.ipynb`

Behaviour:
- outer_fence: very slow update speed (0.001 alpha?) (21,21) gaussian. same threshold
- garden: fast update to adapt with new object position (0.1/0.25 alpha?) (35,35) gaussian. Filter >50. same threshold
- hallway: same option as garden. high filter if many activities. Use low filter in night time. Filter = threshold


'''
MICROSERVICES
- movement_signal.py
    - process image
    - INPUTS:
        - label
        - image in ascending order
        - get folders contents with listdir
        - progress
            in cache/movements/average_value/{timestamp}.hdf5
    - OUTPUTS:
        - store to db
            in movement_signal.db/{label} with timestamp, value
        - store value to cache (temporary)
            in cache/movements/readings/{label}/{timestamp}.cache
        - put progress in
            cache/movements/average_value/{label}/{timestamp}.hdf5
        - get folder contents
            - if >10, keep the last 10
        - run infinite times. sleep(2) in the end of each loop
        
- movement_signal_threshold_updater.py
    - INPUTS:
        - db file in movement_signal.db/{label} with timestamp,value
        - get last 24 hours value from db.
        - run every minute
    - OUTPUTS:
        - file in cache/movements/thresholds/{label}/{timestamp}.cache
        - contains threshold value
        - get folder contents
            - if >10, keep the last 10
    
- movement_signal_alert.py
    - INPUTS:
        - current threshold
            in cache/movements/thresholds/{label}/{timestamp}.cache
            get folder contents. get the last value (newest)
        - current value (filename is timestamp). contains value
            in cache/movements/readings/{label}/{timestamp}.cache
    - OUTPUTS 
        - if value higher than threshold, push to notification worker
        - filename is {timestamp}.cache, Contains value (pass timestamp from previous file)
        - send alert signal in cache/notifications/{label}
            f'{timestamp, converted to %H:%M:%s} {label} val:{value} std:{std} mean:{mean}'
        - after process, delete the cache in cache/movements/readings/{label}/{timestamp}.cache
    
- notifications.py
    - INPUTS:
        - file in cache/notifications/{label}
        - filename (timestamp). contains value
    - OUTPUTS:
        - assign id (sha256)
        - get photo path according to timestamp
            in cache/captured_frames/{label}/{timestamp}.jpg
        - send photo to notification channel
        - send to notifications channel f'{value} id:{sha256[:3]}-{sha256[:-3]}'
        - push value to db: datetime (timestamp from previous), sha256, flag=0 (unflagged), triggered_by (label)
        - send file to cache/proof/{timestamp}.cache, contains sha256
        - delete file in cache/notifications/{movements|vibrations}
    
- proof.py
    - INPUTS:
        - file in cache/proof/
        - sha256 as target dir
        - timestamp from filename
    - OUTPUTS:
        - create new folder in proof/{sha256}/
        - wait until current time is >+30 from timestamp in filename
        - copy file to proof/{sha256}/{timestamps}.jpg
        - delete file in cache/proof/
'''

DEPLOYMENT:
- Make sure firefox installed in "C:\Program Files\Mozilla Firefox\firefox.exe'"
- Make sure geckodriver.exe exist in controller/bin/geckodriver.exe
- create env and update dependencies from /conda_env

Command to run:
- python webcapture.py -u "192.168.0.170" (selenium)
- python webcapture.py -u "192.168.0.207" (selenium)
- python webcapture.py -u "192.168.0.208" (selenium)
- python capture_restructurer.py (base)
- python movement_signal.py -l "outer_fence" (cv2)
- python movement_signal.py -l "hallway" (cv2)
- python movement_signal.py -l "garden" (cv2)
- python movement_signal_threshold_updater.py -l "outer_fence" (base)
- python movement_signal_threshold_updater.py -l "hallway" (base)
- python movement_signal_threshold_updater.py -l "garden" (base)
- python movement_signal_alert.py -l "outer_fence" (base)
- python movement_signal_alert.py -l "hallway" (base)
- python movement_signal_alert.py -l "garden" (base)
- python notifications.py -l "outer_fence" (base)
- python notifications.py -l "hallway" (base)
- python notifications.py -l "garden" (base)
- python proof.py (base)
- python cleanup.py (base)

