""" ref:
https://github.com/ECI-Robotics/opencv_remote_streaming_processing/
"""

import cv2
import configparser
from lib import tracking
from logging import getLogger, basicConfig, DEBUG, INFO
from timeit import default_timer as timer

logger = getLogger(__name__)

basicConfig(
    level=INFO,
    format="%(asctime)s %(levelname)s %(name)s %(funcName)s(): %(message)s")

# load configuration
config = configparser.ConfigParser()
config.read('tello.cfg')
resize_prop = eval(config.get('camera', 'resize_prop'))
flip_code = eval(config.get('camera', 'flip_code'))


class VideoCamera(object):
    def __init__(self, socket, algorithm, target_color, is_stream, is_test,
                 speed, detections):

        # Receive Tello's video streaming.
        # Tello sends video stream to your pc using udp port 11111
        self.cap = cv2.VideoCapture('udp://127.0.0.1:11111')
        ret, frame = self.cap.read()
        self.frame = cv2.resize(frame, resize_prop)
        video_prop = self._get_video_prop()
        logger.info(
            "video_pop:{}, resize_prop:{}".format(video_prop, resize_prop))

        self.tracking = tracking.Tracking(socket, self.frame, video_prop,
                                          algorithm, target_color, is_test,
                                          speed)
        if detections:
            self.detections = detections

    def __del__(self):
        self.cap.release()

    def _get_video_prop(self):
        return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT), self.cap.get(cv2.CAP_PROP_FPS)

    def get_frame(self, is_stream, is_tracking, is_test, speed, is_async_mode,
                  flip_code, is_object_detection, is_face_detection,
                  is_age_gender_detection, is_emotions_detection,
                  is_head_pose_detection, is_facial_landmarks_detection):

        if is_stream or is_tracking:
            ret, frame = self.cap.read()
            frame = cv2.resize(frame, resize_prop)
            if flip_code is not None:
                frame = cv2.flip(frame, flip_code)
            frame = self.tracking.get_track_frame(frame, is_stream, is_test,
                                                  speed)

        if is_object_detection or is_face_detection:
            if is_async_mode:
                ret, next_frame = self.cap.read()
                next_frame = cv2.resize(next_frame, resize_prop)
                if flip_code is not None:
                    next_frame = cv2.flip(next_frame, int(flip_code))
            else:
                ret, frame = self.cap.read()
                frame = cv2.resize(frame, resize_prop)
                next_frame = None
                if flip_code is not None:
                    self.frame = cv2.flip(frame, int(flip_code))
                else:
                    self.frame = frame

            if is_object_detection:
                frame = self.detections.get_det_objects(self.frame, next_frame,
                                                        is_async_mode)
            if is_face_detection:
                frame = self.detections.get_det_faces(
                    self.frame, next_frame, is_async_mode,
                    is_age_gender_detection, is_emotions_detection,
                    is_head_pose_detection, is_facial_landmarks_detection)

        # The first detected frame is None
        if frame is None:
            ret, jpeg = cv2.imencode('1.jpg', self.frame)
        else:
            ret, jpeg = cv2.imencode('1.jpg', frame)

        if is_async_mode and is_object_detection or is_face_detection:
            self.frame = next_frame

        return jpeg.tostring()
