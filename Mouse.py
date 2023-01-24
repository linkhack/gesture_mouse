
import mouse
# import pygame
import screeninfo


class Mouse:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.mouse_listener = None

        monitors = screeninfo.get_monitors()
        default_screen = monitors[0]  # TODO: multiscreen?

        self.h_pixels = default_screen.height
        self.w_pixels = default_screen.width

    def move(self, x: int, y: int, absolute: bool = True):
        if absolute:
            self.x = x
            self.y = y
            mouse.move(x, y, absolute)
        else:
            dx = (x - self.x)
            dy = (y - self.y)
            self.x += dx
            self.y += dy
            mouse.move(dx, dy, absolute)

    def update(self, x, y):
        self.x = x
        self.y = y
        return True

    def process_signal(self, signals):
        # TODO: move this around, possibilities: MosueAction / select signals in demo / select signals in mouse
        updown = "HeadPitch"
        leftright = "HeadYaw"
        y_pixel = self.h_pixels*(1-signals[updown].scaled_value)
        x_pixel = self.w_pixels*(1-signals[leftright].scaled_value)
        self.move(x_pixel, y_pixel)

    def enable_gesture(self):
        pass

    def click(self, button):
        """
        Clicks the mouse button specified with button.
        :param button: str, one of the buttons to click
        :return:
        """
        mouse.click(button)

    def disable_gesture(self):
        pass
