from dataclasses import dataclass

import numpy as np
from PIL import Image
from torchvision import transforms

from ext.img2pose.img2pose import img2poseModel
from ext.img2pose.model_loader import load_model


@dataclass
class Config:
    batch_size: int
    pin_memory: bool
    workers: int
    pose_mean: np.array
    pose_stddev: np.array
    noise_augmentation: bool
    contrast_augmentation: bool
    threed_68_points: str
    distributed: bool


class img2poseEstimator:
    _BBOX_X_FACTOR = 1.1
    _BBOX_Y_FACTOR = 1.1
    _EXPAND_FOREHEAD = 0.3

    _DEPTH = 18
    _MAX_SIZE = 1400
    _MIN_SIZE = 600

    _POSE_MEAN = "ext/img2pose/models/WIDER_train_pose_mean_v1.npy"
    _POSE_STDDEV = "ext/img2pose/models/WIDER_train_pose_stddev_v1.npy"
    _MODEL_PATH = "ext/img2pose/models/img2pose_v1.pth"

    _pose_mean = np.load(_POSE_MEAN)
    _pose_stddev = np.load(_POSE_STDDEV)

    _threed_points = np.load('ext/img2pose/pose_references/reference_3d_68_points_trans.npy')

    _transform = transforms.Compose([transforms.ToTensor()])

    def __init__(self):
        self.img2pose_model = img2poseModel(
            img2poseEstimator._DEPTH, img2poseEstimator._MIN_SIZE, img2poseEstimator._MAX_SIZE,
            pose_mean=img2poseEstimator._pose_mean, pose_stddev=img2poseEstimator._pose_stddev,
            threed_68_points=img2poseEstimator._threed_points,
            bbox_x_factor=img2poseEstimator._BBOX_X_FACTOR,
            bbox_y_factor=img2poseEstimator._BBOX_Y_FACTOR,
            expand_forehead=img2poseEstimator._EXPAND_FOREHEAD,
        )

        load_model(self.img2pose_model.fpn_model, img2poseEstimator._MODEL_PATH, cpu_mode=False, model_only=True)
        self.img2pose_model.evaluate()

    def estimate_pose(self, cv2_img):
        img = Image.fromarray(cv2_img)

        w, h = img.size

        min_size = min(w, h)
        max_size = max(w, h)

        # run on the original image size
        self.img2pose_model.fpn_model.module.set_max_min_size(max_size, min_size)

        res = self.img2pose_model.predict([img2poseEstimator._transform(img)])
        res = res[0]
        pose = res["dofs"].cpu().numpy()[0].astype('float')
        rvec = pose[:3]
        tvec = pose[3:]
        print(tvec)
        return rvec, tvec

