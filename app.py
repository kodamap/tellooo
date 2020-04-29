###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2014 Miguel Grinberg
#
# Released under the MIT license
# https://github.com/miguelgrinberg/flask-video-streaming/blob/master/LICENSE
#
###############################################################################

from flask import Flask, Response, render_template, request, jsonify
from lib.camera import VideoCamera
import argparse
import configparser
import socket
import json
import sys
import threading
import re
from time import sleep
from logging import getLogger, basicConfig, DEBUG, INFO
from lib.args import build_argparser
from lib import interactive_detection
from openvino.inference_engine import get_version

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('tello.cfg')
flip_code = eval(config.get('camera', 'flip_code'))
tello_addr = eval(config.get('tello', 'tello_addr'))
speed = eval(config.get('tello', 'speed'))
config = configparser.ConfigParser()
config.read('color.ini')
colors = config.sections()

logger = getLogger(__name__)
basicConfig(
    level=INFO,
    format="%(asctime)s %(levelname)s %(name)s %(funcName)s(): %(message)s")

distance = 20
move_command = ("up", "down", "left", "right", "back", "forward", "cw", "ccw")

is_connected = False
is_streamon = False
is_stream = True
is_tracking = False
is_test = False
is_async_mode = True
is_object_detection = False
is_face_detection = False
is_age_gender_detection = False
is_emotions_detection = False
is_head_pose_detection = False
is_facial_landmarks_detection = False
flip_code = None  # filpcode: 0,x-axis 1,y-axis -1,both axis
tello_response = ""
devices = None
models = None
detections = None


def send_info(command, tello_response):
    result = {
        "command": command,
        "result": tello_response,
        "is_connected": is_connected,
        "is_streamon": is_streamon,
        "is_stream": is_stream,
        "is_tracking": is_tracking,
        "is_test": is_test,
        "is_async_mode": is_async_mode,
        "flip_code": flip_code,
        "is_object_detection": is_object_detection,
        "is_face_detection": is_face_detection,
        "is_age_gender_detection": is_age_gender_detection,
        "is_emotions_detection": is_emotions_detection,
        "is_head_pose_detection": is_head_pose_detection,
        "is_facial_landmarks_detection": is_facial_landmarks_detection
    }
    logger.info(
        "cmd:{} res:{} con:{} streamon:{} stream:{} tracking:{} test:{} \
        ssd:{} face:{} ag:{} em:{} hp:{} lm:{} async:{} flip:{}"
        .format(command, tello_response, is_connected, is_streamon, is_stream,
                is_tracking, is_test, is_object_detection, is_face_detection,
                is_age_gender_detection, is_emotions_detection,
                is_head_pose_detection, is_facial_landmarks_detection,
                is_async_mode, flip_code))
    return result


def send_command(command):
    command = command.encode(encoding="utf-8")
    s.sendto(command, (tello_addr))
    logger.info("sent:{}".format(command))
    sleep(0.1)


def gen(camera):
    while True:
        frame = camera.get_frame(is_stream, is_tracking, is_test, speed,
                                 is_async_mode, flip_code, is_object_detection,
                                 is_face_detection, is_age_gender_detection,
                                 is_emotions_detection, is_head_pose_detection,
                                 is_facial_landmarks_detection)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/')
def index():
    global is_connected
    global is_streamon

    logger.info(
        "is_connected:{} is_streamon:{}".format(is_connected, is_streamon))
    return render_template(
        'index.html',
        is_streamon=is_streamon,
        is_connected=is_connected,
        is_async_mode=is_async_mode,
        devices=devices,
        models=models,
        enable_detection=enable_detection)


@app.route('/video_feed')
def video_feed():
    camera = VideoCamera(s, algorithm, target_color, is_stream, is_test, speed,
                         detections)
    return Response(
        gen(camera), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/tellooo', methods=['POST'])
def tellooo():
    global is_connected
    global is_streamon
    global speed
    global distance

    command = request.json['command']

    if command in move_command:
        command = command + " " + str(distance)
    if re.search(r'speed \d+', command):
        command = re.search(r'speed \d+', command).group(0)
        speed = int(command.split(" ")[1])
    if re.search(r'distance \d+', command):
        command = re.search(r'distance \d+', command).group(0)
        distance = int(command.split(" ")[1])
    if re.search(r'flip [l,r,f,b]', command):
        command = re.search(r'flip [l,r,f,b]', command).group(0)

    send_command(command)

    if command == 'command' and tello_response == 'ok':
        is_connected = True
    if command == 'streamon' and tello_response == 'ok':
        is_streamon = True
    if command == 'streamoff' and tello_response == 'ok':
        is_streamon = False

    result = send_info(command, tello_response)

    return jsonify(ResultSet=json.dumps(result))


@app.route('/info', methods=['POST'])
def info():
    command = request.json['command']
    send_command(command)
    result = send_info(command, tello_response)
    return jsonify(ResultSet=json.dumps(result))


@app.route('/flip', methods=['POST'])
def flip():
    global flip_code
    command = request.json['command']

    if command == "flip" and flip_code is None:
        flip_code = 0
        tello_response = "around x-axis"
    elif command == "flip" and flip_code == 0:
        flip_code = 1
        tello_response = "around y-axis"
    elif command == "flip" and flip_code == 1:
        flip_code = -1
        tello_response = "around both-axis"
    elif command == "flip" and flip_code == -1:
        flip_code = None
        tello_response = "reset"

    result = send_info(command, tello_response)
    return jsonify(ResultSet=json.dumps(result))


@app.route('/tracking', methods=['POST'])
def tracking():
    global is_stream
    global is_test
    global is_tracking
    global is_object_detection
    global is_face_detection

    tello_response = "on"
    command = request.json['command']

    if command == "streaming":
        is_stream = True
        is_tracking = False
        is_test = False
        is_object_detection = False
        is_face_detection = False
    elif command == "tracking":
        is_stream = False
        is_tracking = True
        is_test = False
        is_object_detection = False
        is_face_detection = False
    elif command == "test":
        is_stream = False
        is_tracking = True
        is_test = True
        is_object_detection = False
        is_face_detection = False

    result = send_info(command, tello_response)
    return jsonify(ResultSet=json.dumps(result))


@app.route('/detection', methods=['POST'])
def detection():
    global is_async_mode
    global is_stream
    global is_tracking
    global is_test
    global is_object_detection
    global is_face_detection
    global is_age_gender_detection
    global is_emotions_detection
    global is_head_pose_detection
    global is_facial_landmarks_detection

    tello_response = "on"
    command = request.json['command']

    if is_object_detection or is_face_detection:
        if command == "async":
            is_async_mode = True
        elif command == "sync":
            is_async_mode = False

    if command == "object_detection":
        is_stream = False
        is_tracking = False
        is_test = False
        is_object_detection = True
        is_face_detection = False
    if command == "face_detection":
        is_stream = False
        is_tracking = False
        is_test = False
        is_object_detection = False
        is_face_detection = True

    if is_face_detection:
        if command == "age_gender_detection":
            is_age_gender_detection = not is_age_gender_detection
        if command == "emotions_detection":
            is_emotions_detection = not is_emotions_detection
        if command == "head_pose_detection":
            is_head_pose_detection = not is_head_pose_detection
        if command == "facial_landmarks_detection":
            is_facial_landmarks_detection = not is_facial_landmarks_detection

    result = send_info(command, tello_response)
    return jsonify(ResultSet=json.dumps(result))


if __name__ == '__main__':

    args = build_argparser().parse_args()

    algorithm = args.algorithm
    target_color = args.color
    is_test = args.test
    enable_detection = args.enable_detection

    if enable_detection:
        devices = [
            args.device, args.device, args.device_age_gender,
            args.device_emotions, args.device_head_pose,
            args.device_facial_landmarks
        ]
        models = [
            args.model_ssd, args.model_face, args.model_age_gender,
            args.model_emotions, args.model_head_pose,
            args.model_facial_landmarks
        ]
        # openvino.inference_engine version '2.1.37988' is openvino_2020.1.033 build
        # , which does not need cpu extension. 
        # https://software.intel.com/en-us/forums/intel-distribution-of-openvino-toolkit/topic/848825
        if "CPU" in devices and args.cpu_extension is None and (get_version() < '2.1.37988'):
            print(
                "\nPlease try to specify cpu extensions library path in demo's command line parameters using -l "
                "or --cpu_extension command line argument")
            sys.exit(1)

        # Create detectors class instance
        detections = interactive_detection.Detections(
            devices, models, args.cpu_extension, args.plugin_dir,
            args.prob_threshold, args.prob_threshold_face, is_async_mode)
        models = detections.models  # Get models to display WebUI.

    # Create a UDP socket to send and receive message with tello
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        host = '0.0.0.0'
        port = 9000
        s.bind((host, port))

        def recv():
            global tello_response
            while True:
                try:
                    tello_response, server = s.recvfrom(1518)
                    tello_response = tello_response.decode(encoding="utf-8")
                    logger.info("res:{}".format(tello_response))
                except Exception:
                    print('\nExit . . .\n')
                    break

        recvThread = threading.Thread(target=recv)
        recvThread.start()

        app.run(host='0.0.0.0', threaded=True)
