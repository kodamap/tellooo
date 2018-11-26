"""
Test without tello. This is socket server for test.

To test video streaming , use ffmpeg.
> ffmpeg -f dshow -i video="Integrated Camera" -preset ultrafast -vcodec libx264 -tune zerolatency -b 900k -f mpegts udp://127.0.0.1:11111
"""

import socket
import re
from time import sleep

battery = 100
speed = 100
temp = 50

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    host = '127.0.0.1'
    port = 50007
    s.bind((host, port))
    print("binding on {}:{}".format(host, port))
    while True:
        data, addr = s.recvfrom(1024)
        data = data.decode(encoding="utf-8")
        print("data: {}, addr: {}".format(data, addr))
        if data == 'battery?':
            battery = battery - 1
            msg = battery
        elif data == 'speed?':
            speed = speed - 1
            msg = speed
        elif data == 'temp?':
            temp = temp + 1
            msg = temp
        elif re.search(r'speed \d+', data):
            msg = re.search(r'speed \d+', data).group(0).split(" ")[1]
        else:
            msg = "ok"
        msg = str(msg).encode(encoding="utf-8")
        sent = s.sendto(msg, ('127.0.0.1', 9000))
