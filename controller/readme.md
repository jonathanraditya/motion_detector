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

## `capture_restructurer.ipynb`
Move, rename, and restructure saved image produced by `webcapture.ipynb`

Behaviour:
- outer_fence: very slow update speed (0.001 alpha?) (21,21) gaussian. same threshold
- garden: fast update to adapt with new object position (0.1/0.25 alpha?) (35,35) gaussian. Filter >50. same threshold
- hallway: same option as garden. high filter if many activities. Use low filter in night time. Filter = threshold
