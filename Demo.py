import dataclasses
import time
from threading import Thread

import keyboard
import mediapipe as mp
import cv2
import numpy as np

from feat.detector import Detector

import Mouse
import DrawingDebug
import SignalsCalculator
import monitor

mp_face_mesh = mp.solutions.face_mesh
mp_face_mesh_connections = mp.solutions.face_mesh_connections


class Demo(Thread):
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.mouse_enabled = False

        self.mouse = Mouse.Mouse()

        self.cam_cap = cv2.VideoCapture(0)
        self.cam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.frame_width, self.frame_height = (1280, 720)

        self.monitor = monitor.monitor()

        self.camera_parameters = (800, 800, 1280/2, 1280/2)
        self.signal_calculator = SignalsCalculator.SignalsCalculater(camera_parameters=self.camera_parameters)
        self.signal_calculator.set_filter_value("screen_xy", 0.022)

        self.detector = Detector()
        # add hotkey
        keyboard.add_hotkey("esc", lambda: self.stop())
        keyboard.add_hotkey("alt + 1", lambda: self.toggle_gesture_mouse())
        # add mouse_events
        self.signal_settings = {
            "pitch": {
                "min": -90,
                "max": +90,
                "filter_value": 0.001
            },
            "yaw": {
                "min": -90,
                "max": +90,
                "filter_value": 0.001
            },
            "roll": {
                "min": -90,
                "max": +90,
                "filter_value": 0.001
            },
            "mouth_open": {
                "min": -90,
                "max": +90,
                "filter_value": 0.001
            }
        }
        self.raw_signal = SignalsCalculator.SignalsResult()
        self.transformed_signals = SignalsCalculator.SignalsResult()

    def run_mediapipe(self):
        self.is_running = True
        with mp_face_mesh.FaceMesh(refine_landmarks=True) as face_mesh:
            while self.is_running and self.cam_cap.isOpened():
                success, image = self.cam_cap.read()
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if not results.multi_face_landmarks:
                    continue
                landmarks = results.multi_face_landmarks[0]
                np_landmarks = np.array(
                    [(lm.x * self.frame_width, lm.y * self.frame_height) for lm in landmarks.landmark])
                result = self.signal_calculator.process(np_landmarks)
                ## Calculate point on screen

                x_pixel, y_pixel = result.screen_xy.get()

                self.raw_signal = result

                if self.mouse_enabled:
                    self.mouse.move(x_pixel, y_pixel, False)
                # Debug
                DrawingDebug.show_landmarks(landmarks, image)
                # DrawingDebug.show_por(x_pixel, y_pixel, self.monitor.w_pixels, self.monitor.h_pixels)

    def run(self):
        self.is_running = True
        with mp_face_mesh.FaceMesh(refine_landmarks=True) as face_mesh:
            while self.is_running and self.cam_cap.isOpened():
                success, image = self.cam_cap.read()
                faces = self.detector.detect_faces(image)
                if not faces:
                    continue
                landmarks = self.detector.detect_landmarks(image, faces)
                pose = self.detector.detect_facepose(image, landmarks)
                aus = self.detector.detect_aus(image, landmarks)

                self.raw_signal.jaw_open.set(aus[0][0,17])
                self.raw_signal.mouth_puck.set(aus[0][0,12])
                print(aus)



    def record_neutral(self):
        with mp_face_mesh.FaceMesh(refine_landmarks=True) as face_mesh:
            success, image = self.cam_cap.read()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if not results.multi_face_landmarks:
                return False

            landmarks = results.multi_face_landmarks[0]
            np_landmarks = np.array(
                [(lm.x * self.frame_width, lm.y * self.frame_height) for lm in
                 landmarks.landmark])
            self.signal_calculator.process_neutral(np_landmarks)

            return True

    def stop(self):
        self.is_running = False
        self.cam_cap.release()

    def disable_gesture_mouse(self):
        # Disables gesture mouse and enables normal mouse input
        self.mouse_enabled = False
        self.mouse.disable_gesture()

    def enable_gesture_mouse(self):
        # Disables normal mouse and enables gesture mouse
        self.mouse_enabled = True
        self.mouse.enable_gesture()

    def toggle_gesture_mouse(self):
        # Toggles between gesture and normal mouse
        if self.mouse_enabled:
            self.disable_gesture_mouse()
        else:
            self.enable_gesture_mouse()

    def set_filter_value(self, name: str, filter_value: float):
        print(name)
        self.signal_calculator.set_filter_value(name, filter_value)
