from logging import getLogger, basicConfig, DEBUG, INFO
import threading
import configparser
from time import time, sleep

logger = getLogger(__name__)
basicConfig(
    level=INFO,
    format="%(asctime)s %(levelname)s %(name)s %(funcName)s(): %(message)s")
"""load config"""
config = configparser.ConfigParser()
config.read('tello.cfg')
tello_addr = eval(config.get('tello', 'tello_addr'))
right = eval(config.get('tello', 'right'))
left = eval(config.get('tello', 'left'))
up = eval(config.get('tello', 'up'))
down = eval(config.get('tello', 'down'))
back = eval(config.get('tello', 'back'))
forward = eval(config.get('tello', 'forward'))
cw = eval(config.get('tello', 'cw'))
ccw = eval(config.get('tello', 'ccw'))
move_interval = eval(config.get('tello', 'move_interval'))
rotate_interval = eval(config.get('tello', 'rotate_interval'))
move_ratio_threshold = eval(config.get('tello', 'move_ratio_threshold'))
min_area = eval(config.get('tracking', 'min_area'))
back_ratio = eval(config.get('tracking', 'back_ratio'))
forward_ratio = eval(config.get('tracking', 'forward_ratio'))
pos_limit = eval(config.get('tracking', 'position_limit'))


class TelloMove(object):
    def __init__(self, socket, is_test, speed):
        self.s = socket
        self.is_test = is_test
        self.sent_command = 'speed'
        self.xpos, self.ypos, self.zpos, self.rotate = [0, 0, 0, 0]
        self.xpos_limit, self.ypos_limit, self.zpos_limit, self.rotate_limit = pos_limit
        """ create initail thread """
        self.t = threading.Thread(
            target=self._send_msg,
            args=((self.sent_command, speed), move_interval, self.is_test))
        self.t.start()

    def _calc_current_position(self, command, move_distance):
        if command == "left":
            self.xpos = self.xpos + move_distance
        if command == "right":
            self.xpos = self.xpos - move_distance
        if command == "up":
            self.ypos = self.ypos + move_distance
        if command == "down":
            self.ypos = self.ypos - move_distance
        if command == "back":
            self.zpos = self.zpos + move_distance
        if command == "forward":
            self.zpos = self.zpos - move_distance
        if command == "cw":
            self.rotate = self.rotate + move_distance
        if command == "ccw":
            self.rotate = self.rotate - move_distance
        logger.debug("command:{} current x:{} y:{} z:{} rotate:{}".format(
            command, self.xpos, self.ypos, self.zpos, self.rotate))
        return

    def current_position(self):
        return (self.xpos, self.ypos, self.zpos, self.rotate)

    def _send_msg(self, *args):
        logger.debug("args:{}, len:{}".format(args, len(args)))
        """parse arg
          args : ex. Thread (('cw', 20), 0.1, True)
        """
        command = args[0][0]
        interval = args[1]
        if len(args[0]) == 1:
            move_distance = 0
            msg = command
        else:
            move_distance = args[0][1]
            msg = command + " " + str(move_distance)
        msg = msg.encode(encoding="utf-8")
        if not self.is_test:
            self.s.sendto(msg, (tello_addr))
        self._calc_current_position(command, move_distance)
        logger.info("{}, msg:{} interval:{} is_test:{}".format(
            threading.current_thread().name, msg, interval, self.is_test))
        sleep(interval)

    def _move_tello(self, command, track_area_ratio):
        if not self.t.is_alive():
            if command in ('cw', 'ccw'):
                interval = rotate_interval
            else:
                interval = move_interval
            self.t = threading.Thread(
                target=self._send_msg,
                args=((command, eval(command)[0]), interval, self.is_test))
            self.t.start()
        self.sent_command = command

    def motion(self, track_window, track_area_ratio, move_ratio, margin_window,
               is_test):
        """ initialize tello's position when tracking mode changes"""
        if self.is_test != is_test:
            self.xpos, self.ypos, self.zpos, self.rotate = [0, 0, 0, 0]
        self.is_test = is_test
        """ x, y, w, h: current positon of track window.
            xmin, ymin, xmax, ymax : position of margin window.
        """
        x, y, w, h = track_window
        xmin, ymin, xmax, ymax = margin_window
        """ Nothing to be done when tracking object might be failed """
        if x < xmin and x + w > xmax or y < ymin and y + h > ymax:
            logger.debug(
                "trackin might be failed: track_window area is larger than \
                margin_window area: track_window:{}, margin_window:{}"
                .format(track_window, margin_window))
            return
        elif track_window[2] * track_window[3] < min_area:
            logger.debug(
                "tacking might be failed: track_window area is smaller than \
                min_area w:{}, h:{}".format(w, h))
            return
        """ starts moving back and forward motion """
        command = ""
        if track_area_ratio < back_ratio[1]:
            if self.zpos < self.zpos_limit:
                command = "back"
        elif track_area_ratio > forward_ratio[0]:
            if self.zpos > self.zpos_limit * -1:
                command = "forward"
        if command:
            self._move_tello(command, track_area_ratio)
            return
        """ right, left and rotate motion
            cw / ccw would make move_raito high. Checking sent command prevents tello from confusing.
        """
        if x < xmin:
            if abs(move_ratio[0]) < move_ratio_threshold[0]:
                if self.rotate < self.rotate_limit:
                    command = "cw"
            elif self.sent_command not in ('cw', 'ccw'):
                if self.xpos > self.xpos_limit * -1:
                    command = "right"
        if x > xmax - w:
            if abs(move_ratio[0]) < move_ratio_threshold[0]:
                if self.rotate > self.rotate_limit * -1:
                    command = "ccw"
            elif self.sent_command not in ('cw', 'ccw'):
                if self.xpos < self.xpos_limit:
                    command = "left"
        if command:
            self._move_tello(command, track_area_ratio)
        """ up and down motion """
        if y < ymin:
            if self.ypos < self.ypos_limit:
                command = "up"
        if y > ymax - h:
            if self.ypos > self.ypos_limit * -1:
                command = "down"
        if command:
            self._move_tello(command, track_area_ratio)
