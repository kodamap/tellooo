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
from camera import VideoCamera
import argparse
import configparser
import socket
import json
import threading
import re
from time import sleep
from logging import getLogger, basicConfig, DEBUG, INFO

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

streamon, connected, detection = False, False, False
distance = 20

tello_response = ""
move_command = ("up", "down", "left", "right", "back", "forward", "cw", "ccw")


def send_command(command):
    command = command.encode(encoding="utf-8")
    s.sendto(command, (tello_addr))
    logger.info("sent:{}".format(command))
    sleep(0.1)


def gen(camera):
    while True:
        frame = camera.get_frame(stream_only, is_test, speed, detection,
                                 is_flip)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/')
def index():
    global connected
    global streamon

    logger.info("connected:{} streamon:{}".format(connected, streamon))
    return render_template(
        'index.html',
        streamon=streamon,
        connected=connected,
        enable_detection=enable_detection)


@app.route('/video_feed')
def video_feed():
    camera = VideoCamera(s, algorithm, target_color, stream_only, is_test,
                         speed, device, enable_detection)
    return Response(
        gen(camera), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/tracking', methods=['POST'])
def tracking():
    global connected
    global streamon
    global stream_only
    global is_test
    global detection
    tello_response = ""
    command = request.json['command']
    if command == "streamonly":
        stream_only, is_test, detection = True, False, False
    elif command == "tracking":
        stream_only, is_test, detection = False, False, False
    elif command == "test":
        stream_only, is_test, detection = False, True, False
    elif command == "detection":
        stream_only, is_test, detection = False, False, True
    result = {
        "command": command,
        "result": tello_response,
        "connected": connected,
        "streamon": streamon,
        "detection": detection
    }
    logger.info(
        "sent:{} res:{} con:{} stream:{} detection:{} is_filp_y: {}".format(
            command, tello_response, connected, streamon, detection, is_flip))
    return jsonify(ResultSet=json.dumps(result))


@app.route('/tellooo', methods=['POST'])
def tellooo():
    global connected
    global streamon
    global tello_response
    global speed
    global distance
    tello_response = ""
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
        connected = True
    if command == 'streamon' and tello_response == 'ok':
        streamon = True
    if command == 'streamoff' and tello_response == 'ok':
        streamon = False
    result = {
        "command": command,
        "result": tello_response,
        "connected": connected,
        "streamon": streamon
    }
    logger.info(
        "sent:{} res:{} con:{} stream:{} detection:{} is_filp_y: {}".format(
            command, tello_response, connected, streamon, detection, is_flip))
    return jsonify(ResultSet=json.dumps(result))


@app.route('/info', methods=['POST'])
def info():
    global connected
    global streamon
    global tello_response
    tello_response = ""
    command = request.json['command']
    send_command(command)
    result = {
        "command": command,
        "result": tello_response,
        "connected": connected,
        "streamon": streamon
    }
    logger.info(
        "sent:{} res:{} con:{} stream:{} detection:{} is_filp_y: {}".format(
            command, tello_response, connected, streamon, detection, is_flip))
    return jsonify(ResultSet=json.dumps(result))


@app.route('/flip', methods=['POST'])
def flip():
    global is_flip
    command = request.json['command']
    if command == "flip-y":
        is_flip = not is_flip
    result = {
        "command": command,
        "result": tello_response,
        "connected": connected,
        "streamon": streamon,
        "is_flip": is_flip
    }
    logger.info(
        "sent:{} res:{} con:{} stream:{} detection:{} is_filp_y: {}".format(
            command, tello_response, connected, streamon, detection, is_flip))
    return jsonify(ResultSet=json.dumps(result))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='opencv object tracking with tello')
    parser.add_argument(
        '-a',
        '--algorithm',
        help='selct object tracking algorithm',
        default='camshift',
        choices=['camshift', 'meanshift'])
    parser.add_argument(
        '-s',
        '--stream_only',
        help='stream mode (without object traking)',
        action='store_true')
    parser.add_argument(
        '-t',
        '--test',
        help='test mode (without moving arms)',
        action='store_true')
    parser.add_argument(
        '-c',
        '--color',
        help='select tracking color in color.ini',
        default='',
        choices=colors)
    parser.add_argument(
        "-d",
        "--device",
        help="Specify the target device to infer on; CPU, GPU, FPGA or MYRIAD is acceptable. Demo "
        "will look for a suitable plugin for device specified (CPU by default)",
        default="CPU",
        type=str)
    parser.add_argument(
        '--enable_detection',
        help='enable object detection using MobileNet-SSD',
        action='store_true')
    args = parser.parse_args()

    algorithm = args.algorithm
    target_color = args.color
    stream_only = args.stream_only
    is_test = args.test
    device = args.device
    enable_detection = args.enable_detection
    if flip_code == 1:
        is_flip = True
    else:
        is_flip = False
    """ Create a UDP socket to send and receive message with tello """
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
