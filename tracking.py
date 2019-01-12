import cv2
import camshift
import meanshift
import detection
import configparser
import tellolib
import threading
from time import sleep
import math
from timeit import default_timer as timer
""" load configuration """
config = configparser.ConfigParser()
config.read('tello.cfg')
frame_prop = eval(config.get('camera', 'frame_prop'))
frame_margin = eval(config.get('camera', 'frame_margin'))
track_area = eval(config.get('tracking', 'track_area'))
track_interval = eval(config.get('tracking', 'track_interval'))
detect_interval = eval(config.get('tracking', 'detect_interval'))


class Tracking(object):
    def __init__(self, socket, ret, frame, video_prop, algorithm, target_color,
                 is_test, speed, device, enable_detection):
        next_frame = frame
        self.track_frame = None
        self.is_test = is_test
        self.speed = speed
        self.init_track_window = self._set_track_window()
        self.track_window = self.init_track_window
        self.track_window0 = self.track_window
        self.margin_window = self._set_margin_window()
        """ Create tello instnace """
        self.tello = tellolib.TelloMove(socket, self.is_test, speed)
        """ Create opencv tracking instnace """
        if algorithm == "meanshift":
            self.tracking = meanshift.MeanShift(
                frame_prop, self.ini_track_window, target_color)
        else:
            self.tracking = camshift.CamShift(
                frame_prop, self.init_track_window, target_color)
        self.t = threading.Thread(target=self._start_track, args=(ret, frame))
        self.t.start()
        """ Create object detection instnace """
        if enable_detection:
            self.detection = detection.ObjectDetection(frame_prop, device)
            self.d = threading.Thread(
                target=self._start_detection, args=(frame, next_frame))
            self.d.start()
        """ Set text put on frames """
        self.video_params = "video:({}, {} fps:{}) resize:{}".format(
            round(video_prop[0]),
            round(video_prop[1]), round(video_prop[2]), frame_prop, self.speed)
        self.config_params = "interval:{} margin:{} {} {}".format(
            track_interval, frame_margin, algorithm, target_color)
        self.track_data = "track window:{}({}) {}".format(0, 0, 0)
        self.position = "current pos:{}({})".format(0, 0)
        """ initialize FPS """
        self.accum_time = 0
        self.curr_fps = 0
        self.fps = "FPS: ??"
        self.prev_time = timer()

    def _set_margin_window(self):
        frame_width, frame_height = frame_prop
        xmargin = frame_width * frame_margin
        ymargin = frame_height * frame_margin
        return xmargin, ymargin, frame_width - xmargin, frame_height - ymargin

    def _set_track_window(self):
        frame_width, frame_height = frame_prop
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

    def _calc_fps(self):
        # Calculate FPS
        curr_time = timer()
        exec_time = curr_time - self.prev_time
        self.prev_time = curr_time
        self.accum_time = self.accum_time + exec_time
        self.curr_fps = self.curr_fps + 1
        if self.accum_time > 1:
            self.accum_time = self.accum_time - 1
            self.fps = "FPS: " + str(self.curr_fps)
            self.curr_fps = 0
        return self.fps

    def _start_track(self, *args):
        ret = args[0]
        frame = args[1]
        self.track_frame, self.track_window, self.track_window0 = self.tracking.object_tracking(
            ret, frame)
        track_area_ratio = self._calc_track_area_ratio(self.track_window,
                                                       track_area)
        move_ratio = self._calc_move_ratio(self.track_window,
                                           self.track_window0)
        self.tello.motion(self.track_window, track_area_ratio, move_ratio,
                          self.margin_window, self.is_test)
        init_track_area = track_area[0] * track_area[1]
        track_window_area = self.track_window[2] * self.track_window[3]
        self.track_data = "track win:{} area:({}/{} {})".format(
            self.track_window, init_track_area, track_window_area,
            track_area_ratio)
        current_position = self.tello.current_position()
        self.position = "current pos:{} move_ratio:({}, {})".format(
            current_position, abs(move_ratio[0]), abs(move_ratio[1]))
        sleep(track_interval)
        """ update current fps """
        self._calc_fps()

    def _start_detection(self, *args):
        frame = args[0]
        next_frame = args[1]
        self.track_frame = self.detection.start_inference(frame, next_frame)
        sleep(detect_interval)
        """ update current fps """
        self._calc_fps()

    def get_track_frame(self, ret, frame, stream_only, is_test, speed,
                        detection):
        self.is_test = is_test
        self.speed = speed

        if stream_only:
            self.track_frame = frame
            mode = ("streamon", (0, 0, 0))
            self.fps = self._calc_fps()
        elif is_test:
            mode = ("is_test", (0, 128, 0))
        elif detection:
            mode = ("detection", (0, 0, 0))
        else:
            mode = ("tracking", (0, 0, 255))

        if not stream_only and not detection:
            if not self.t.is_alive():
                self.t = threading.Thread(
                    target=self._start_track, args=(ret, frame))
                self.t.start()
            """ draw margin window on the frame """
            xmin, ymin, xmax, ymax = self.margin_window
            cv2.rectangle(self.track_frame, (round(xmin), round(ymin)),
                          (round(xmax), round(ymax)), mode[1], 1)
            """ draw init window on the frame """
            init_xmin = self.init_track_window[0]
            init_ymin = self.init_track_window[1]
            init_xmax = self.init_track_window[0] + self.init_track_window[2]
            init_ymax = self.init_track_window[1] + self.init_track_window[3]
            cv2.rectangle(
                self.track_frame, (round(init_xmin), round(init_ymin)),
                (round(init_xmax), round(init_ymax)), (128, 255, 255), 1)
            cv2.putText(self.track_frame, self.config_params, (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
            cv2.putText(self.track_frame, self.track_data, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
            cv2.putText(self.track_frame, self.position, (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)

        if detection:
            # No threading detection cause too much dropped frame.
            ##next_frame = frame
            ##self.track_frame = self.detection.start_inference(frame, next_frame)
            ##frame = next_frame
            next_frame = frame
            if not self.d.is_alive():
                self.d = threading.Thread(
                    target=self._start_detection, args=(frame, next_frame))
                self.d.start()
                frame = next_frame

        # always show video prames in the frame
        cv2.putText(self.track_frame, self.video_params, (10, 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
        mode_and_speed = "MODE:{} ".format(mode[0])
        cv2.rectangle(self.track_frame,
                      (frame_prop[0] - 100, frame_prop[1] - 20), (frame_prop),
                      (255, 255, 255), -1)
        cv2.putText(self.track_frame, mode_and_speed,
                    (frame_prop[0] - 97, frame_prop[1] - 7),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, mode[1], 1)

        # Draw FPS in top left corner
        cv2.rectangle(self.track_frame, (frame_prop[0] - 50, 0),
                      (frame_prop[0], 17), (255, 255, 255), -1)
        cv2.putText(self.track_frame, self.fps, (frame_prop[0] - 47, 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 1)

        return self.track_frame
