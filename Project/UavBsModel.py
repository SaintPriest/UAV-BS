import math
import time
import numpy as np
import random
import copy
from vpython import vec


class UavBsModel:
    def __init__(self, hexagon_length, uavs):
        self.uavs = uavs
        self.ues = []
        self.ues_backup = []
        self.ground = Ground(hexagon_length)
        self.center = copy.deepcopy(uavs[len(uavs) // 2].position)
        random.Random().seed(time.time())

        # Simulation window parameters
        r = hexagon_length  # radius of disk
        xx0 = self.center.x
        yy0 = self.center.z  # centre of disk

        # Simulate Poisson point process
        point_num = 3000  # Poisson number of points
        theta = 2 * np.pi * np.random.uniform(0, 1, point_num)  # angular coordinates
        rho = r * np.sqrt(np.random.uniform(0, 1, point_num))  # radial coordinates

        # Convert from polar to Cartesian coordinates
        xx = rho * np.cos(theta)
        yy = rho * np.sin(theta)

        # Shift centre of disk to (xx0,yy0)
        ue_xx = xx + xx0
        ue_yy = yy + yy0

        for ue_x, ue_y in zip(ue_xx, ue_yy):
            self.ues.append(vec(ue_x, 0, ue_y))

        self.ues_backup = copy.deepcopy(self.ues)

    def set_ue_num(self, num):
        if num < len(self.ues):
            del self.ues[num:]
        elif num > len(self.ues):
            for i in range(len(self.ues), num):
                self.ues.append(self.ues_backup[i])


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
    def __init__(self, hexagon_length):
        self.hexagon_length = hexagon_length


if __name__ == '__main__':
    uav = Uav(position=(1, 2))
    print(uav.radius)
