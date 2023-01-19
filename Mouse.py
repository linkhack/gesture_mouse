
import mouse
import pygame


class Mouse:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.mouse_listener = None

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

    def enable_gesture(self):
        pass

    def disable_gesture(self):
        pass
