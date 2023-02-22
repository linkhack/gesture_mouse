import cv2

def test_read_image():
    cam_cap = cv2.VideoCapture(0)
    cam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cam_cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P',
                                                                 'G'))  # From https://forum.opencv.org/t/videoio-v4l2-dev-video0-select-timeout/8822/4 for linux
    while cam_cap.isOpened():
        success, image = cam_cap.read()
        print(image)
        print(success)