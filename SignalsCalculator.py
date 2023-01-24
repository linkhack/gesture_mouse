import DrawingDebug
from PnPHeadPose import PnPHeadPose
from face_geometry import PCF, get_metric_landmarks
import monitor
import KalmanFilter1D

from scipy.spatial.transform import Rotation
import numpy as np
import cv2

from dataclasses import dataclass, fields
from numbers import Number


class FilteredFloat:
    def __init__(self, value: Number, filter_value: float = None):
        if filter_value is None:
            self.use_filter = False
            self.filter_R = 0.
        else:
            self.use_filter = True
            self.filter_R = filter_value
        self.filter = KalmanFilter1D.Kalman1D(R=self.filter_R**2)
        self.value = value

    def set(self, value):
        """
        Adds a new value to be filtered and returns the filtered value
        :param value: New value to be filtered
        """
        if self.use_filter:
            kalman = self.filter.update(value)
            self.value = np.real(kalman)
        else:
            self.value = value
        return self.value

    def get(self):
        return self.value

    def set_filter_value(self, filter_value):
        self.filter_R = filter_value
        self.use_filter = True
        self.filter = KalmanFilter1D.Kalman1D(R=self.filter_R ** 2)


class Filtered2D:
    def __init__(self, value: np.ndarray((2,)), filter_value: float = None):
        if filter_value is None:
            self.use_filter = False
            self.filter_R = 0.
        else:
            self.use_filter = True
            self.filter_R = filter_value
        self.filter = KalmanFilter1D.Kalman1D(R=self.filter_R ** 2)
        self.value = value

    def set(self, value):
        if self.use_filter:
            kalman = self.filter.update(value[0]+1j*value[1])
            self.value[0], self.value[1] = (np.real(kalman), np.imag(kalman))
        else:
            self.value = value

    def get(self):
        return self.value

    def set_filter_value(self, filter_value):
        if filter_value > 0:
            self.use_filter = True
            self.filter = KalmanFilter1D.Kalman1D(R=filter_value ** 2)
        else:
            self.use_filter = False


@dataclass
class SignalsResult:
    rvec: np.ndarray
    tvec: np.ndarray
    nosetip: np.ndarray
    pitch: FilteredFloat
    yaw: FilteredFloat
    roll: FilteredFloat
    screen_xy: Filtered2D
    jaw_open: FilteredFloat
    mouth_puck: FilteredFloat
    debug1: FilteredFloat
    debug2: FilteredFloat
    debug3: FilteredFloat

    def __init__(self):
        self.rvec = np.zeros((3,))
        self.tvec = np.zeros((3,))
        self.nosetip = np.zeros((3,))
        self.pitch = FilteredFloat(0.)
        self.yaw = FilteredFloat(0.)
        self.roll = FilteredFloat(0.)
        self.jaw_open = FilteredFloat(0.)
        self.mouth_puck = FilteredFloat(0.)
        self.debug1 = FilteredFloat(0.)
        self.debug2 = FilteredFloat(0.)
        self.debug3 = FilteredFloat(0.)
        self.screen_xy = Filtered2D(np.zeros((2,)))


class SignalsCalculater:
    def __init__(self, camera_parameters):
        self.result = SignalsResult()
        self.neutral_landmarks = np.zeros((478, 3))
        self.camera_parameters = camera_parameters
        self.head_pose_calculator = PnPHeadPose()
        self.monitor = monitor.monitor()

    def process(self, landmarks):
        rvec, tvec = self.head_pose(landmarks[:, :2])

        r = Rotation.from_rotvec(np.squeeze(rvec))

        rotationmat = r.as_matrix()
        angles = r.as_euler("xyz", degrees=True)
        #normalized_landmarks = rotationmat.T@(landmarks-tvec.T)
        self.result.rvec = rvec # TODO: result not needed anymore
        self.result.tvec = tvec
        self.result.yaw.set(angles[1])
        self.result.pitch.set(angles[0])
        self.result.roll.set(angles[2])
        self.result.nosetip = rotationmat@self.head_pose_calculator.canonical_metric_landmarks[1, :]+tvec.squeeze()
        jaw_open = self.get_jaw_open(landmarks)
        self.result.jaw_open.set(jaw_open)
        mouth_puck = self.get_mouth_puck(landmarks)
        self.result.mouth_puck.set(mouth_puck)
        screen_xy = self.get_screen_intersection()
        screen_xy = np.array(screen_xy)
        self.result.screen_xy.set(screen_xy)

        signals = {
            "Pitch": angles[0],
            "Yaw": angles[1],
            "Roll": angles[2],
            "JawOpen": jaw_open,
            "MouthPuck": mouth_puck
        }

        return signals

    def process_neutral(self, landmarks):
        pass

    def head_pose(self, landmarks):
        rvec, tvec = self.head_pose_calculator.fit_func(landmarks, self.camera_parameters)
        return rvec, tvec

    def get_screen_intersection(self):
        rotation_matrix, _ = cv2.Rodrigues(self.result.rvec)
        forward = np.matmul(rotation_matrix, np.array([0., 0., -1.]))
        screen_point = self.result.nosetip - self.result.nosetip[2]/forward[2] * forward
        x_pixel, y_pixel = self.monitor.camera_to_monitor(10*screen_point[0], 10*screen_point[1])
        return x_pixel, y_pixel

    def get_jaw_open(self, landmarks):
        mouth_distance = np.linalg.norm(landmarks[14, :]-landmarks[13, :])
        nose_tip = landmarks[1, :]
        chin_moving_landmark = landmarks[18, :]
        head_height = np.linalg.norm(landmarks[10, :]-landmarks[151, :])
        jaw_nose_distance = np.linalg.norm(nose_tip-chin_moving_landmark)
        normalized_distance = jaw_nose_distance/head_height
        return normalized_distance

    def get_mouth_puck(self, landmarks):
        left_distance = np.linalg.norm(landmarks[302]-landmarks[72])
        d = np.linalg.norm(landmarks[151, :] - landmarks[10, :])
        normalized_distance = left_distance/d
        return normalized_distance

    def set_filter_value(self, field_name: str, filter_value: float):
        signal = getattr(self.result, field_name, None)
        if signal is not None:
            signal.set_filter_value(filter_value)
