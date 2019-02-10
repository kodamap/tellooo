###############################################################################
#                          License Agreement
#               For Open Source Computer Vision Library
#                       (3-clause BSD License)
#
# Copyright (C) 2000-2018, Intel Corporation, all rights reserved.
# Copyright (C) 2009-2011, Willow Garage Inc., all rights reserved.
# Copyright (C) 2009-2016, NVIDIA Corporation, all rights reserved.
# Copyright (C) 2010-2013, Advanced Micro Devices, Inc., all rights reserved.
# Copyright (C) 2015-2016, OpenCV Foundation, all rights reserved.
# Copyright (C) 2015-2016, Itseez Inc., all rights reserved.
# Third party copyrights are property of their respective owners.
# 
# Released under the MIT license
# https://github.com/opencv/opencv/blob/master/LICENSE
# 
###############################################################################

import numpy as np
import cv2
import configparser


class MeanShift(object):
    def __init__(self, track_window, target_color):
        # set up initial location of window
        self.track_window = track_window
        self.term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10,
                          1)
        self.target_color = target_color
        if self.target_color:
            config = configparser.ConfigParser()
            config.read('color.ini')
            # define range of color in HSV
            self.lower_color = [
                int(c) for c in config[target_color]['lower'].split(',')
            ]
            self.upper_color = [
                int(c) for c in config[target_color]['upper'].split(',')
            ]

    def object_tracking(self, frame):
        # begin object tracking
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        if self.target_color:
            # Threshold the HSV image to get only blue colors
            mask = cv2.inRange(hsv,
                               np.array(self.lower_color),
                               np.array(self.upper_color))
        else:
            mask = cv2.inRange(hsv,
                               np.array((0., 60., 32.)),
                               np.array((180., 255., 255.)))

        x, y, w, h = self.track_window
        hsv_roi = hsv[y:y + h, x:x + w]
        mask_roi = mask[y:y + h, x:x + w]
        hist = cv2.calcHist([hsv_roi], [0], mask_roi, [16], [0, 180])
        cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
        self.hist = hist.reshape(-1)

        prob = cv2.calcBackProject([hsv], [0], self.hist, [0, 180], 1)
        prob &= mask

        # get location before apply meanshift
        track_window0 = self.track_window

        # apply meanshift to get the new location
        ret, self.track_window = cv2.meanShift(prob, self.track_window,
                                               self.term_crit)

        # Draw it on image
        x, y, w, h = self.track_window
        frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Draw frame margin on image
        xmin, ymin, xmax, ymax = self.margin_window
        frame = cv2.rectangle(frame, (round(xmin), round(ymin)),
                              (round(xmax), round(ymax)), (0, 0, 255), 1)

        # Draw track critelia on image
        xtrack_min, ytrack_min, xtrack_max, ytrack_max = self.critelia
        frame = cv2.rectangle(frame, (round(xtrack_min), round(ytrack_min)),
                              (round(xtrack_max), round(ytrack_max)),
                              (128, 255, 255), 1)

        return frame, self.track_window, track_window0
