import random

class ScreenShake:
    def __init__(self):
        self.duration = 0
        self.intensity = 5

    def start(self, duration, intensity=5):
        self.duration = duration
        self.intensity = intensity

    def update(self):
        if self.duration > 0:
            self.duration -= 1
            offset_x = random.randint(-self.intensity, self.intensity)
            offset_y = random.randint(-self.intensity, self.intensity)
            return offset_x, offset_y
        return 0, 0