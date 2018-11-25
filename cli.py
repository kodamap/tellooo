import socket
import shlex
from subprocess import CREATE_NEW_CONSOLE, Popen
import configparser
import threading

config = configparser.ConfigParser()
config.read('tello.cfg')
tello_addr = eval(config.get('tello', 'tello_addr'))

config = configparser.ConfigParser()
config.read('color.ini')
colors = config.sections()


def tracking():

    while True:
        print("you can select colors:{} or input:['s or stream', 't or test']".
              format(colors))
        color = input("\r\ncolor: ")
        if color in ('stream', 's'):
            command = "python tracking.py --stream_only"
        elif color in ('test', 't'):
            color = input("\r\ncolor(test): ")
            if color not in colors:
                continue
            command = "python tracking.py --test -c " + str(color)
        elif color not in colors:
            continue
        else:
            command = "python tracking.py -c " + str(color)
        args = shlex.split(command)
        p = Popen(args, creationflags=CREATE_NEW_CONSOLE)
        print("\n browse http://<your pc ip>:5000/video_feed\n")
        return p


def send_msg(msg, s):
    msg = msg.encode(encoding="utf-8")
    s.sendto(msg, (tello_addr))
    print("command: {}".format(msg))


if __name__ == '__main__':

    print('Tello Python3 Demo. tello addr: {}'.format(tello_addr))
    print('end -- quit demo.\r\n')
    """key mapping"""
    key_map = {
        'c': 'command',
        'f': 'left',
        'a': 'right',
        'e': 'up',
        'x': 'down',
        's': 'forward',
        'd': 'back',
        'r': 'ccw',
        'w': 'cw',
        't': 'takeoff',
        'tt': 'land',
        'v': 'streamon',
        'vv': 'streamoff',
        'b': 'battery?'
    }
    """Create a UDP socket"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        host = '0.0.0.0'
        port = 9000
        s.bind((host, port))

        def recv():
            while True:
                try:
                    data, server = s.recvfrom(1518)
                    print(data.decode(encoding="utf-8"))
                except Exception:
                    print('\nExit . . .\n')
                    break

        #recvThread create
        recvThread = threading.Thread(target=recv)
        recvThread.start()

        while True:
            try:
                msg = input("")
                if not msg:
                    continue
                if 'end' in msg:
                    print('...')
                    s.close()
                    break
                if msg == 'h':
                    print(key_map)
                try:
                    if msg in ('c', 'v', 'vv', 't', 'tt', 'b'):
                        msg = key_map[msg]
                    elif len(msg) == msg.count(msg[0]):
                        distance = 20 * len(msg)
                        msg = key_map[msg[0]]
                        msg = msg + " " + str(distance)
                except:
                    pass
                send_msg(msg, s)
                if msg == 'streamon':
                    p = tracking()
                elif msg == 'streamoff':
                    p.terminate()
                    print("stream ended")
            except KeyboardInterrupt:
                print('\n . . .\n')
                s.close()
                break
