import math
import time
import numpy as np
import random
import copy
from vpython import vec

class UavBsModel:
    def __init__(self, length, width):
        self.uavs = []
        self.backup_ues = []
        self.ground = Ground(length, width)
        random.Random().seed(time.time())

        # Convert from polar to Cartesian coordinates
        xx = np.random.uniform(0, 1, 2000)
        yy = np.random.uniform(0, 1, 2000)

        # Shift centre of disk to (xx0,yy0)
        xx = xx * length
        yy = yy * width

        for ue_x, ue_y in zip(xx, yy):
            self.backup_ues.append(vec(ue_x, 0, ue_y))
        self.ues = copy.deepcopy(self.backup_ues)

    def set_ue_num(self, num):
        if num < len(self.ues):
            del self.ues[num:]
        elif num > len(self.ues):
            for i in range(len(self.ues), num):
                self.ues.append(self.backup_ues[i])


class Uav:
    def __init__(self, position, height, theta=math.pi / 3):
        self.position = position
        self.height = height
        self.theta = theta
        self.radius = 0
        self.update_radius()

    def update_radius(self):
        self.radius = self.height * (1 / math.tan(self.theta))


class Ground:
    def __init__(self, length, width):
        self.length = length
        self.width = width


if __name__ == '__main__':
    uav = Uav(position=(1, 2))
    print(uav.radius)
