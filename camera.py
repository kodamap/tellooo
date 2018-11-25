import cv2
import camshift
import meanshift
import configparser
import tellolib
import threading
from time import time, sleep
import math
"""locad config"""
config = configparser.ConfigParser()
config.read('tello.cfg')
frame_prop = eval(config.get('camera', 'frame_prop'))
frame_margin = eval(config.get('camera', 'frame_margin'))
flipcode = eval(config.get('camera', 'flipcode'))
track_area = eval(config.get('tracking', 'track_area'))
track_interval = eval(config.get('tracking', 'track_interval'))


class VideoCamera(object):
    def __init__(self, socket, algorithm, target_color, stream_only, is_test):
        """Receive Tello video streaming.
           Tello sends video stream to your pc using udp port 11111. 
        """
        self.video = cv2.VideoCapture('udp://127.0.0.1:11111')
        self.video_prop = self._get_video_prop()
        self.stream_only = stream_only
        self.is_test = is_test
        self.init_track_window = self._set_track_window()
        self.track_window = self.init_track_window
        self.track_window0 = self.track_window
        self.margin_window = self._set_margin_window()
        self.tello = tellolib.TelloMove(socket, is_test)
        if algorithm == "meanshift":
            self.tracking = meanshift.MeanShift(
                frame_prop, self.ini_track_window, target_color)
        else:
            self.tracking = camshift.CamShift(
                frame_prop, self.init_track_window, target_color)
        self.params = "{}*{}({}) {} intvl:{} margin:{} {} {}".format(
            self.video_prop[0], self.video_prop[1], self.video_prop[2],
            frame_prop, track_interval, frame_margin, algorithm, target_color)
        self.track_data = "track window:{}({}) {}".format(0, 0, 0)
        self.position = "current pos:{}({})".format(0, 0)
        ret, self.frame = self.video.read()
        self.t = threading.Thread(
            target=self._tracking, args=(ret, self.frame))
        self.t.start()

    def __del__(self):
        self.video.release()

    def _get_video_prop(self):
        return self.video.get(cv2.CAP_PROP_FRAME_WIDTH), self.video.get(
            cv2.CAP_PROP_FRAME_HEIGHT), self.video.get(cv2.CAP_PROP_FPS)

    def _set_margin_window(self):
        frame_width, frame_height = frame_prop[:-1]
        xmargin = frame_width * frame_margin
        ymargin = frame_height * frame_margin
        return xmargin, ymargin, frame_width - xmargin, frame_height - ymargin

    def _set_track_window(self):
        frame_width, frame_height = frame_prop[:-1]
        xtrack = frame_width / 2 - (track_area[0] / 2)
        ytrack = frame_height / 2 - (track_area[1] / 2)
        return int(xtrack), int(ytrack), track_area[0], track_area[1]

    def _calc_move_ratio(self, track_window, track_window0):
        x, y, w, h = track_window
        x0, y0, w0, h0 = track_window0
        diff = (x0 - x, y0 - y, w0 - w, h0 - h)
        move_ratio = (round(diff[0] / frame_prop[0], 2),
                      round(diff[1] / frame_prop[1], 2))
        return move_ratio

    def _calc_track_area_ratio(self, track_window, track_area):
        track_area = track_area[0] * track_area[1]
        track_window_area = track_window[2] * track_window[3]
        return round(math.sqrt(track_area) / math.sqrt(track_window_area), 2)

    def _tracking(self, *args):
        ret = args[0]
        self.frame = args[1]
        self.frame, self.track_window, self.track_window0 = self.tracking.object_tracking(
            ret, self.frame)
        track_area_ratio = self._calc_track_area_ratio(self.track_window,
                                                       track_area)
        move_ratio = self._calc_move_ratio(self.track_window,
                                           self.track_window0)
        self.tello.motion(self.track_window, track_area_ratio, move_ratio,
                          self.margin_window, self.is_test)
        self.track_data = "track win:{} area:({}/{} {}) speed:{}".format(
            self.track_window, track_area[0] * track_area[1],
            self.track_window[2] * self.track_window[3], track_area_ratio,
            self.tello.speed)
        current_position = self.tello.current_position()
        self.position = "current pos:{} ({}, {})".format(current_position,
                                                         abs(move_ratio[0]),
                                                         abs(move_ratio[1]))
        sleep(track_interval)

    def get_frame(self, stream_only, is_test):
        self.stream_only = stream_only
        self.is_test = is_test
        if is_test:
            mode = ("test", (0, 128, 0))
        else:
            mode = ("tracking", (0, 0, 255))
        ret, self.frame = self.video.read()
        self.frame = cv2.resize(
            cv2.flip(self.frame, flipcode), (frame_prop[0], frame_prop[1]))
        if not self.stream_only:
            ##self._tracking(ret, self.frame)
            if not self.t.is_alive():
                self.t = threading.Thread(
                    target=self._tracking, args=(ret, self.frame))
                self.t.start()
            x, y, w, h = self.track_window
            self.frame = cv2.rectangle(self.frame, (x, y), (x + w, y + h),
                                       (255, 0, 0), 2)
            xmin, ymin, xmax, ymax = self.margin_window
            self.frame = cv2.rectangle(self.frame, (round(xmin), round(ymin)),
                                       (round(xmax), round(ymax)), mode[1], 1)
            init_xmin = self.init_track_window[0]
            init_ymin = self.init_track_window[1]
            init_xmax = self.init_track_window[0] + self.init_track_window[2]
            init_ymax = self.init_track_window[1] + self.init_track_window[3]
            self.frame = cv2.rectangle(
                self.frame, (round(init_xmin), round(init_ymin)),
                (round(init_xmax), round(init_ymax)), (128, 255, 255), 1)
            self.frame = cv2.putText(
                self.frame,
                self.params, (10, 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.25, (255, 255, 255),
                thickness=1)
            self.frame = cv2.putText(
                self.frame,
                self.track_data, (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.3, (255, 255, 255),
                thickness=1)
            self.frame = cv2.putText(
                self.frame,
                self.position, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.3, (255, 255, 255),
                thickness=1)
            self.frame = cv2.putText(
                self.frame,
                "mode:" + mode[0], (10, frame_prop[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.3,
                mode[1],
                thickness=1)
        ret, jpeg = cv2.imencode('1.jpg', self.frame)
        return jpeg.tostring()
