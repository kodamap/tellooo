""" ref:
https://github.com/ECI-Robotics/opencv_remote_streaming_processing/
"""

import cv2
import configparser
import tracking
""" load configuration """
config = configparser.ConfigParser()
config.read('tello.cfg')
frame_prop = eval(config.get('camera', 'frame_prop'))
flip_code = eval(config.get('camera', 'flip_code'))


class VideoCamera(object):
    def __init__(self, socket, algorithm, target_color, stream_only, is_test,
                 speed, device, enable_detection):
        """ Receive Tello's video streaming.
            Tello sends video stream to your pc using udp port 11111
        """
        self.video = cv2.VideoCapture('udp://127.0.0.1:11111')
        ret, frame = self.video.read()
        frame = cv2.resize(frame, frame_prop)
        if ret:
            video_prop = self._get_video_prop()
            self.tracking = tracking.Tracking(socket, ret, frame, video_prop,
                                              algorithm, target_color, is_test,
                                              speed, device, enable_detection)

    def __del__(self):
        self.video.release()

    def _get_video_prop(self):
        return self.video.get(cv2.CAP_PROP_FRAME_WIDTH), self.video.get(
            cv2.CAP_PROP_FRAME_HEIGHT), self.video.get(cv2.CAP_PROP_FPS)

    def get_frame(self, stream_only, is_test, speed, detection, is_flip):
        ret, frame = self.video.read()
        frame = cv2.resize(frame, frame_prop)
        if is_flip:
            frame = cv2.flip(frame, flip_code)
        frame = self.tracking.get_track_frame(ret, frame, stream_only, is_test,
                                              speed, detection)
        if not ret:
            return

        ret, jpeg = cv2.imencode('1.jpg', frame)

        return jpeg.tostring()
