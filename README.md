# Object tracking with Tello 

## What's this

This is test code of object tracking with Tello.

You can do followings:
* Video streaming from Tello on your browser.
* Object / Color Tracking.
* Change caputure mode (streamonly, test, tracking).

[![](https://img.youtube.com/vi/5qkPdTKIr74/0.jpg)](https://www.youtube.com/watch?v=5qkPdTKIr74)

browser image


<a href="https://raw.githubusercontent.com/wiki/kodamap/tracking_Tello/images/Tellooo_Pooh.jpg">
<img src="https://raw.githubusercontent.com/wiki/kodamap/tracking_Tello/images/Tellooo_Pooh.jpg" alt="kibana dashboard" style="width:auto;height:auto;" ></a>



## Reference

* Tello SDK Documentation (v1.3)
Commands this app used are  based on sdk v1.3

https://dl-cdn.ryzerobotics.com/downloads/Tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf


* Flask Video streaming

http://blog.miguelgrinberg.com/post/video-streaming-with-flask

https://github.com/ECI-Robotics/opencv_remote_streaming_processing/


##  Environment (tested on Windows10)

* Python 3.6.x
* Flask 0.12.2
* opencv-python 3.4.3.18
* Chrome / Firefox

## Required Packages

Install required packages with pip 

```sh
pip install -r requirements.txt
```

or

```sh
pip install opencv-python
pip install flask
```

## How to use

Command Option

```sh
$ python app.py -h
usage: app.py [-h] [-a {camshift,meanshift}] [-s] [-t]
              [-c {blue,red,yellow,green}]

opencv object tracking with tello

optional arguments:
  -h, --help            show this help message and exit
  -a {camshift,meanshift}, --algorithm {camshift,meanshift}
                        selct object tracking algorithm
  -s, --stream_only     stream mode (without object traking)
  -t, --test            test mode (without moving arms)
  -c {blue,red,yellow,green}, --color {blue,red,yellow,green}
                        select tracking color in color.ini
```

### Object tracking settings (parameters in Tello.cfg)

* frame property

```sh
[camera]
# deifne frame resolution and frame rate.
# (320 * 240  16fps is recommend)
# Note: This is resize prameter of frames. OpenCV VideoCapture with udp streaming can not set cv2.CAP_PROP_XX.
frame_prop = (320, 240, 16)
.
.
```

* Tello setting 

```sh
[Tello]
# Tello address and port is not needed to change. 
# You can change this when you test udp socket on your pc. (see test\server.py)
# Tello_addr = ('127.0.0.1', 50007)
Tello_addr = ('192.168.10.1', 8889)
# define move cm by operation (MIN, MAX, Tello sdk MAX)
right = (20, 30, 500)
left = (20, 30, 500)
.
.
```

* tracking setting

Note:
* **Verify the motion limit range of Tello for your safety.**
'position_limit' (used with tracking mode) is not the actual position of Tello but the position calcurated by this applicaiton per sending command to Tello. 

```sh
[tracking]
.
.
# !! important !! set the motion limit range of Tello for your safety 
#  (x, y, z (cm), rotate (dgree))
position_limit = (300, 300, 300, 180)
```


### Run app

1. Power on the Tello.
1. Connect to Tello's wifi network (TELLO-XXXXXX)
1. Run app (ex. Color tracking with test mode.)
```sh
$ python app.py --test --color yellow
```
4. Access to the streaming url on your browser
```sh
http://127.0.0.1:5000/
```
5. connet to Tello (click the connect button)

Note: 
* if you can not connect Tello (no response:ok ) , make sure to be connected Tello's network and try to restart app (Stop(Ctl + C) , then run app again).
* "test mode" means that 'object tracking' is enabled but **Tello moving ('sending command to Tello') is disabled**.


colors are defined  in color.ini

```sh
# define hsv (hue, staturation, lightness)
[yellow]
lower = 20, 100, 100
upper = 40, 255, 255
.
.
```


## Misc

### Test on your PC

Modify 'Tello_addr' of '[Tello]' section in Tello.cfg.

```sh
[Tello]
Tello_addr = ('127.0.0.1', 50007)
```

To test video streaming , use ffmpeg.

```sh
$ ffmpeg -f dshow -i video="Integrated Camera" -preset ultrafast -vcodec libx264 -tune zerolatency -b 900k -f mpegts udp://127.0.0.1:11111
```

### Store bootstrap and jQuery on your pc

You need to store bootstrap and jQuery on your pc (see static/js , static/css)
because you have not internet connection while connectiong to Tello's wifi network.

Tested with these version:
* jquery-3.3.1
* bootstrap-4.1.3