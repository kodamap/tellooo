# Object tracking with Tello 

## What's this

This is test code of object tracking with Tello.

You can do followings:
* Video streaming from Tello on your browser.
* Object / Color Tracking.
* Change tracking mode (streamonly, test, tracking).
* Object detection (OpenVINO environment is required)

Face detection demo (YouTube Link)

[![](https://img.youtube.com/vi/I6-YKfPHo_g/0.jpg)](https://www.youtube.com/watch?v=I6-YKfPHo_g)


Color tracking (YouTube Link)

[![](https://img.youtube.com/vi/5qkPdTKIr74/0.jpg)](https://www.youtube.com/watch?v=5qkPdTKIr74)


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
* OpenVINO Toolkit R4/R5 (Required only when object/face detection is enanbled )

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
usage: app.py [-h] [-a {camshift,meanshift}] [-t] [-tr]
              [-c {blue,skyblue,red,yellow,green}] [--enable_detection]
              [-m_ss MODEL_SSD] [-m_fc MODEL_FACE] [-m_ag MODEL_AGE_GENDER]
              [-m_em MODEL_EMOTIONS] [-m_hp MODEL_HEAD_POSE]
              [-m_lm MODEL_FACIAL_LANDMARKS] [-l CPU_EXTENSION]
              [-d {CPU,GPU,FPGA,MYRIAD}] [-d_ag {CPU,GPU,FPGA,MYRIAD}]
              [-d_em {CPU,GPU,FPGA,MYRIAD}] [-d_hp {CPU,GPU,FPGA,MYRIAD}]
              [-d_lm {CPU,GPU,FPGA,MYRIAD}] [-pp PLUGIN_DIR] [--labels LABELS]
              [-pt PROB_THRESHOLD] [-ptf PROB_THRESHOLD_FACE]

optional arguments:
  -h, --help            show this help message and exit
  -a {camshift,meanshift}, --algorithm {camshift,meanshift}
                        selct object tracking algorithm
  -t, --test            test mode (without tracking motion)
  -tr, --tracking       test mode (without tracking motion)
  -c {blue,skyblue,red,yellow,green}, --color {blue,skyblue,red,yellow,green}
                        select tracking color in color.ini
  --enable_detection    enable object detection using MobileNet-SSD
  -m_ss MODEL_SSD, --model_ssd MODEL_SSD
                        Required. Path to an .xml file with a trained
                        MobileNet-SSD model.
  -m_fc MODEL_FACE, --model_face MODEL_FACE
                        Optional. Path to an .xml file with a trained
                        Age/Gender Recognition model.
  -m_ag MODEL_AGE_GENDER, --model_age_gender MODEL_AGE_GENDER
                        Optional. Path to an .xml file with a trained
                        Age/Gender Recognition model.
  -m_em MODEL_EMOTIONS, --model_emotions MODEL_EMOTIONS
                        Optional. Path to an .xml file with a trained Emotions
                        Recognition model.
  -m_hp MODEL_HEAD_POSE, --model_head_pose MODEL_HEAD_POSE
                        Optional. Path to an .xml file with a trained Head
                        Pose Estimation model.
  -m_lm MODEL_FACIAL_LANDMARKS, --model_facial_landmarks MODEL_FACIAL_LANDMARKS
                        Optional. Path to an .xml file with a trained Facial
                        Landmarks Estimation model.
  -l CPU_EXTENSION, --cpu_extension CPU_EXTENSION
                        MKLDNN (CPU)-targeted custom layers.Absolute path to a
                        shared library with the kernels impl.
  -d {CPU,GPU,FPGA,MYRIAD}, --device {CPU,GPU,FPGA,MYRIAD}
                        Specify the target device for MobileNet-SSSD / Face
                        Detection to infer on; CPU, GPU, FPGA or MYRIAD is
                        acceptable.
  -d_ag {CPU,GPU,FPGA,MYRIAD}, --device_age_gender {CPU,GPU,FPGA,MYRIAD}
                        Specify the target device for Age/Gender Recognition
                        to infer on; CPU, GPU, FPGA or MYRIAD is acceptable.
  -d_em {CPU,GPU,FPGA,MYRIAD}, --device_emotions {CPU,GPU,FPGA,MYRIAD}
                        Specify the target device for for Emotions Recognition
                        to infer on; CPU, GPU, FPGA or MYRIAD is acceptable.
  -d_hp {CPU,GPU,FPGA,MYRIAD}, --device_head_pose {CPU,GPU,FPGA,MYRIAD}
                        Specify the target device for Head Pose Estimation to
                        infer on; CPU, GPU, FPGA or MYRIAD is acceptable.
  -d_lm {CPU,GPU,FPGA,MYRIAD}, --device_facial_landmarks {CPU,GPU,FPGA,MYRIAD}
                        Specify the target device for Facial Landmarks
                        Estimation to infer on; CPU, GPU, FPGA or MYRIAD is
                        acceptable.
  -pp PLUGIN_DIR, --plugin_dir PLUGIN_DIR
                        Path to a plugin folder
  --labels LABELS       Labels mapping file
  -pt PROB_THRESHOLD, --prob_threshold PROB_THRESHOLD
                        Probability threshold for object detections filtering
  -ptf PROB_THRESHOLD_FACE, --prob_threshold_face PROB_THRESHOLD_FACE
                        Probability threshold for face detections filtering
```

### Object tracking settings (parameters in Tello.cfg)

* frame property

```sh
[camera]
# deifne resize property of frame.
# (480 * 360  is recommend)
# Note: This is resize prameter of frames. OpenCV VideoCapture with udp streaming can not set cv2.CAP_PROP_XX.
resize_prop = (480, 360)
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

<a href="https://raw.githubusercontent.com/wiki/kodamap/tellooo/images/color_tracking.jpg">
<img src="https://raw.githubusercontent.com/wiki/kodamap/tellooo/images/color_tracking.jpg" alt="pooh" style="width:auto;height:auto;" ></a>

Note: 
* if you can not connect to Tello (no response:ok ) , make sure to connect Tello's network and try to restart app (Stop(Ctrl + C) , then run app again).
* Red buttons (arrow icons) send flip motion command to Tello. Be careful around!
* "test mode" means that 'object tracking' is enabled but ** motion of Tello (sending command to Tello) is disabled **.


colors are defined  in color.ini

```sh
# define hsv (hue, staturation, lightness)
[yellow]
lower = 20, 100, 100
upper = 40, 255, 255
.
.
```

## Object detection mode

You can test Object deteciton using MobileNet-SSD (detection button). Detection mode requires OpenVINO Toolkit R4/R5 installed on your PC and CPU extension dll ,IR files bellow.

### Requirements
* Install Intel® Distribution of OpenVINO™ toolkit for Windows* 10
https://software.intel.com/en-us/articles/OpenVINO-Install-Windows

* URL: https://drive.google.com/open?id=1YKbwy9W0MZObls9dy_0n90MQoRq0RdOB
  * File extension.zip
  * Size: 32,084,333 byte
  * MD5 hash : 31d7c77ade31fd1cb9cca6c9a92128f3

* Extract extension.zip and store extension folder under the "tellooo"

```sh
extension/cpu_extension.dll
extension/IR/MobileNetSSD_FP16/MobileNetSSD_deploy.bin
extension/IR/MobileNetSSD_FP16/MobileNetSSD_deploy.mapping
extension/IR/MobileNetSSD_FP16/MobileNetSSD_deploy.xml
extension/IR/MobileNetSSD_FP32/MobileNetSSD_deploy.bin
extension/IR/MobileNetSSD_FP32/MobileNetSSD_deploy.mapping
extension/IR/MobileNetSSD_FP32/MobileNetSSD_deploy.xml
```

3. Download Face detection models IR files

```sh
cd extension/IR/
models="face-detection-retail-0004 age-gender-recognition-retail-0013 emotions-recognition-retail-0003 head-pose-estimation-adas-0001 landmarks-regression-retail-0009"
for model in $models
do
wget --no-check-certificate https://download.01.org/openvinotoolkit/2018_R5/open_model_zoo/${model}/FP16/${model}.xml
wget --no-check-certificate https://download.01.org/openvinotoolkit/2018_R5/open_model_zoo/${model}/FP16/${model}.bin
done
```

### Run App

1. Run app (ex. Color tracking with test mode AND enable object detection.)
```sh
$ python app.py --test --color yellow --enable_detection
```
* If you use MYRIAD plugin (NCS2（Neural Compute Stick2))
```sh
$ python app.py --test --color yellow --enable_detection --device MYRIAD
```
2. Access to the streaming url on your browser
```sh
http://127.0.0.1:5000/
```

<a href="https://raw.githubusercontent.com/wiki/kodamap/tellooo/images/object_detection.jpg">
<img src="https://raw.githubusercontent.com/wiki/kodamap/tellooo/images/object_detection.jpg" alt="detection" style="width:auto;height:auto;" ></a>



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
