import time
from valkka.core import *


# filter_3 = InfoFrameFilter("filter_3")
# filter_2 = InfoFrameFilter("filter_2", filter_3)
# live_out_filter = InfoFrameFilter("live_out_filter", filter_2)
# livethread = LiveThread("livethread")

# Forking FrameFilters
# branch 1
info_filter = InfoFrameFilter("info_filter")
gate_filter = GateFrameFilter("gate_filter", info_filter)

# branch 2
file_filter = FileFrameFilter("file_filter")

# main branch
live_out_filter = ForkFrameFilter("live_out_filter", gate_filter, file_filter)
livethread = LiveThread("livethread")



rtsp_address = "rtsp://admin:Valerian%40live1@192.168.0.208:554/Streaming/Channels/101/"
rtsp_address = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4"

ctx = LiveConnectionContext(LiveConnectionType_rtsp, rtsp_address, 1, live_out_filter)

# close the gate before streaming
gate_filter.unSet()

livethread.startCall()
livethread.registerStreamCall(ctx)
livethread.playStreamCall(ctx)
time.sleep(20)

print("Start writing to disk")
file_filter.activate("stream.mkv")
time.sleep(20)

print("let's get verbose")
gate_filter.set()
time.sleep(10)

print("close file and exit")
file_filter.deActivate()

livethread.stopCall()

print("bye")