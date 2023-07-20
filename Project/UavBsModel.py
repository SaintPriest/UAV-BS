import math
import time
import numpy as np
import random
import copy
from vpython import vec


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def in_hexagon(origin, point, hexagon_length):
    ue_x = point[0]
    ue_y = point[1]
    a = np.linalg.norm((ue_x - origin.x, ue_y - origin.z))
    b = hexagon_length
    c = np.linalg.norm((ue_x - (origin.x + hexagon_length), ue_y - origin.z))
    theta = math.acos((a ** 2 + b ** 2 - c ** 2) / (2 * a * b))
    if ue_y - origin.z < 0:
        theta = math.pi * 2 - theta

    while theta > math.pi / 3:
        ue_x, ue_y = rotate((origin.x, origin.z), (ue_x, ue_y), -math.pi / 3)
        theta -= math.pi / 3

    # to polar
    ue_x -= origin.x
    ue_y -= origin.z
    A = (hexagon_length, 0)
    AB = (hexagon_length / 2, -hexagon_length * math.sqrt(3) / 2)
    AP = (A[0] - ue_x, A[1] - ue_y)
    if np.cross(AB, AP) >= 0:
        return True
    return False


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
            if in_hexagon(self.center, (ue_x, ue_y), hexagon_length):
                self.ues_backup.append(vec(ue_x, 0, ue_y))
                if len(self.ues_backup) == 2000:
                    break

        self.ues = copy.deepcopy(self.ues_backup)

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
