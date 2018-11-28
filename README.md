# Object tracking with Tello 

## What's this

This is test code of object tracking with Tello.

You can do followings:
* Video streaming from Tello on your browser.
* Object / Color Tracking.
* Change tracking mode (streamonly, test, tracking).

[![](https://img.youtube.com/vi/5qkPdTKIr74/0.jpg)](https://www.youtube.com/watch?v=5qkPdTKIr74)

browser image

<a href="https://raw.githubusercontent.com/wiki/kodamap/tellooo/images/tellooo_s.jpg">
<img src="https://raw.githubusercontent.com/wiki/kodamap/tellooo/images/tellooo_s.jpg" alt="start" style="width:auto;height:auto;" ></a>

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
[tello]
# tello address and port is not needed to change.
tello_addr = ('192.168.10.1', 8889)
# define move cm by operation (MIN, MAX, Tello sdk MAX)
right = (20, 30, 500)
left = (20, 30, 500)
.
.
```

* tracking setting

```sh
[tracking]
.
.
# !! important !! set the motion limit range of Tello for your safety 
#  (x, y, z (cm), rotate (dgree))
position_limit = (300, 300, 300, 180)
```

Note:
* **Verify the motion limit range of Tello for your safety.**
position_limit is not the actual position of Tello but the position calcurated by this applicaiton per sending command to Tello. 



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

<a href="https://raw.githubusercontent.com/wiki/kodamap/tellooo/images/tellooo_p.jpg">
<img src="https://raw.githubusercontent.com/wiki/kodamap/tellooo/images/tellooo_p.jpg" alt="pooh" style="width:auto;height:auto;" ></a>

Note: 
* if you can not connect to Tello (no response:ok ) , make sure to connect Tello's network and try to restart app (Stop(Ctrl + C) , then run app again).
* Red buttons (arrow icons) send flip motion command to Tello, be careful around!
* "test mode" means that 'object tracking' is enabled but **Tello moving (sending command to Tello) is disabled**.


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

Modify 'Tello_addr' of '[Tello]' section in tello.cfg.
You can change this when you test udp video streaming on your pc. (see test\server.py)

```sh
[tello]
tello_addr = ('127.0.0.1', 50007)
```

To test video streaming , use ffmpeg.

```sh
$ ffmpeg -f dshow -i video="Integrated Camera" -preset ultrafast -vcodec libx264 -tune zerolatency -b 900k -f mpegts udp://127.0.0.1:11111
```

### Video capture does not display

Make sure firewall settings on your PC.  Tello sends video stream  to your PC via udp port 11111, which is needed to be open.

### Store bootstrap and jQuery on your pc

bootstrap, jQuery and font awesome are stored locally since you have no internet connection while connecting Tello. (see static/js , static/css)

Tested with these version:
* jquery-3.3.1
* bootstrap-4.1.3
* font awesome-free-5.5.0
* popper.js-1.14.5 (umd)
