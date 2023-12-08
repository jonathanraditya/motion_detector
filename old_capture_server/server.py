import time
from valkka.core import *

# YUV => RGB interpolation to the small size is done each 1000 milliseconds and passed on to the shmem ringbuffer
image_interval=1000  
# define rgb image dimensions
width  =1280//4
height =720//4
# posix shared memory: identification tag and size of the ring buffer
shmem_name    ="cam_example" 
shmem_buffers =10 

shmem_filter    =RGBShmemFrameFilter(shmem_name, shmem_buffers, width, height)
sws_filter      =SwScaleFrameFilter("sws_filter", width, height, shmem_filter)
interval_filter =TimeIntervalFrameFilter("interval_filter", image_interval, sws_filter)

avthread        =AVThread("avthread",interval_filter)
av_in_filter    =avthread.getFrameFilter()
livethread      =LiveThread("livethread")

ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4", 1, av_in_filter)

avthread.startCall()
livethread.startCall()

avthread.decodingOnCall()
livethread.registerStreamCall(ctx)
livethread.playStreamCall(ctx)

# all those threads are written in cpp and they are running in the
# background.  Sleep for 20 seconds - or do something else while
# the cpp threads are running and streaming video
time.sleep(40)

# stop threads
livethread.stopCall()
avthread.stopCall()

print("bye") 