from collections import deque
import time


class FPSCounter:
    """
    Class for counting fps. Averages the last n frame times.
    usage counter = FPSCounter(). Then call fps=counter() one time per frame
    """

    def __init__(self, length: int):
        """
        Constructor for fps counter
        Args:
            length: fps over the last length frames
        """
        self.time_counter = deque(maxlen=length)

    def __call__(self):
        """
        Call the counter to add another frame time.
        Returns:
                FPS average of the last length frame
        """
        self.time_counter.append(time.time())
        if len(self.time_counter) > 1:
            return len(self.time_counter) / (self.time_counter[-1] - self.time_counter[0])
        else:
            return 0.0
