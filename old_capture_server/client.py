import cv2
from valkka.api2 import ShmemRGBClient

width  =1280//4
height =720//4

# This identifies posix shared memory - must be same as in the server side
shmem_name    ="cam_example"
# Size of the shmem ringbuffer - must be same as in the server side
shmem_buffers =10              

client=ShmemRGBClient(
name          =shmem_name,
n_ringbuffer  =shmem_buffers,
width         =width,
height        =height,
mstimeout     =1000,        # client timeouts if nothing has been received in 1000 milliseconds
verbose       =False
) 

while True:
    index, isize = client.pull()
if (index==None):
    print("timeout")
else:
    data =client.shmem_list[index][0:isize]
    img =data.reshape((height,width,3))
    img =cv2.GaussianBlur(img, (21, 21), 0)
    cv2.imshow("valkka_opencv_demo",img)
    cv2.waitKey(1)