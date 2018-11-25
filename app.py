from flask import Flask, Response, render_template, request, jsonify
from camera import VideoCamera
import argparse
import configparser
import socket
import json
import threading
from time import sleep
from logging import getLogger, basicConfig, DEBUG, INFO

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('tello.cfg')
tello_addr = eval(config.get('tello', 'tello_addr'))
config = configparser.ConfigParser()
config.read('color.ini')
colors = config.sections()

logger = getLogger(__name__)
basicConfig(
    level=INFO,
    format="%(asctime)s %(levelname)s %(name)s %(funcName)s(): %(message)s")

streamon = False
connected = False
tello_response = ""
move_command = ("up", "down", "left", "right", "back", "forward", "cw", "ccw")


def send_command(command):
    command = command.encode(encoding="utf-8")
    s.sendto(command, (tello_addr))
    logger.info("sent:{}".format(command))
    sleep(0.1)


def gen(camera):
    while True:
        frame = camera.get_frame(stream_only, is_test)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/')
def index():
    global connected
    global streamon
    logger.info("connected: {} streamon:{}".format(connected, streamon))
    return render_template(
        'index.html', streamon=streamon, connected=connected)


@app.route('/video_feed')
def video_feed():
    camera = VideoCamera(s, algorithm, target_color, stream_only, is_test)
    return Response(
        gen(camera), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/tracking', methods=['POST'])
def tracking():
    global connected
    global streamon
    global stream_only
    global is_test
    tello_response = ""
    command = request.json['command']
    if command == "streamonly":
        stream_only = True
        is_test = False
    elif command == "tracking":
        stream_only = False
        is_test = False
    elif command == "test":
        stream_only = False
        is_test = True
    result = {"command": command, "result": tello_response, "connected": connected, "streamon": streamon}
    logger.info("sent:{} res:{} con:{} stream:{}".format(command, tello_response, connected, streamon))
    return jsonify(ResultSet=json.dumps(result))


@app.route('/tellooo', methods=['POST'])
def tellooo():
    global connected
    global streamon
    global tello_response
    tello_response = ""
    command = request.json['command']
    if command == 'streamon':
        streamon = True
    if command == 'streamoff':
        streamon = False
    if command in move_command:
        command = command + " 20"  # hard coded mininum motion 20 cm/degree
    send_command(command)
    if command == 'command' and tello_response == 'ok':
        connected = True
    result = {"command": command, "result": tello_response, "connected": connected, "streamon": streamon}
    logger.info("sent:{} res:{} con:{} stream:{}".format(command, tello_response, connected, streamon))
    return jsonify(ResultSet=json.dumps(result))


@app.route('/info', methods=['POST'])
def info():
    global connected
    global streamon
    global tello_response
    tello_response = ""
    command = request.json['command']
    send_command(command)
    result = {"command": command, "result": tello_response, "connected": connected, "streamon": streamon}
    logger.info("sent:{} res:{} con:{} stream:{}".format(command, tello_response, connected, streamon))
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
    args = parser.parse_args()

    algorithm = args.algorithm
    target_color = args.color
    stream_only = args.stream_only
    is_test = args.test
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
