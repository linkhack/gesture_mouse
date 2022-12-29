#!/usr/bin/env python3

# --------------------------------------------------------
# Copyright (C) 2020 NVIDIA Corporation. All rights reserved.
# NVIDIA Source Code License (1-Way Commercial)
# Code written by Shalini De Mello.
# --------------------------------------------------------

import screeninfo
import numpy as np


class monitor:

    def __init__(self):
        monitors = screeninfo.get_monitors()
        default_screen = monitors[0]  # TODO: multiscreen?

        self.h_mm = default_screen.height_mm
        self.w_mm = default_screen.width_mm

        self.h_pixels = default_screen.height
        self.w_pixels = default_screen.width

        self.h_ppmm = self.h_pixels / self.h_mm
        self.w_ppmm = self.w_pixels / self.w_mm
        self.ppmm = (self.h_ppmm + self.w_ppmm) / 2

    def monitor_to_camera(self, x_pixel, y_pixel):
        # assumes in-build laptop camera, located centered and 10 mm above display
        # update this function for you camera and monitor using: https://github.com/computer-vision/takahashi2012cvpr
        x_cam_mm = ((int(self.w_pixels / 2) - x_pixel) / self.w_pixels) * self.w_mm
        y_cam_mm = 9.5 + (y_pixel / self.h_pixels) * self.h_mm
        z_cam_mm = 0.0

        return x_cam_mm, y_cam_mm, z_cam_mm

    def camera_to_monitor(self, x_cam_mm, y_cam_mm):
        # assumes in-build laptop camera, located centered and 10 mm above display
        # update this function for you camera and monitor using: https://github.com/computer-vision/takahashi2012cvpr
        x_mon_pixel = np.ceil(int(self.w_pixels / 2) - x_cam_mm * self.w_pixels / self.w_mm)
        y_mon_pixel = np.ceil((y_cam_mm - 9.5) * self.h_pixels / self.h_mm)
        return x_mon_pixel, y_mon_pixel

    def pixel_to_mm(self, pixels):
        return pixels / self.ppmm

    def mm_to_pixel(self, mm):
        return mm * self.ppmm
