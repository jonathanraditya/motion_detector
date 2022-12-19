# Server backend controller
## `global_modules.py`
Globally used classes and functions.

## `microcontroller_server.py`
Server for vibration_server microcontroller. This would enable microcontroller to store readings (`/input`) and get output (`/output`) to the server.

## `webcapture.ipynb`
Modify `webcapture.py` by modifying the .ipynb file and exporting as "executeable script".

Run in conda terminal with `env:selenium` to create a single capture server.
Use `python webcapture.py` with `-u <urlhost>` parameter. 
Three urlhost to pass (one for each capture server):
- 192.168.0.170 -> outer_fence
- 192.168.0.207 -> hallway
- 192.168.0.208 -> garden

