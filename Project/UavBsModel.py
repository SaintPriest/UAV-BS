import math
import numpy as np;
from vpython import vec

class UavBsModel:
    def __init__(self, length, width):
        self.uavs = []
        self.ues = []
        self.ground = Ground(length, width)
        # Simulation window parameters
        r = 1  # radius of disk
        xx0 = 0
        yy0 = 0  # centre of disk
        areaTotal = np.pi * r ** 2  # area of disk

        # Point process parameters
        lambda0 = 100  # intensity (ie mean density) of the Poisson process

        # Simulate Poisson point process
        numbPoints = np.random.poisson(lambda0 * areaTotal)  # Poisson number of points
        theta = 2 * np.pi * np.random.uniform(0, 1, numbPoints)  # angular coordinates
        rho = r * np.sqrt(np.random.uniform(0, 1, numbPoints))  # radial coordinates

        # Convert from polar to Cartesian coordinates
        xx = rho * np.cos(theta)
        yy = rho * np.sin(theta)

        # Shift centre of disk to (xx0,yy0)
        ue_xx = (xx + xx0) * (length / 2) + self.ground.length / 2
        ue_yy = (yy + yy0) * (width / 2) + self.ground.width / 2

        for ue_x, ue_y in zip(ue_xx, ue_yy):
            self.ues.append(vec(ue_x, 0, ue_y))


class Uav:
    def __init__(self, position, height, theta=math.pi / 3, radius=None):
        self.position = position
        self.height = height
        self.theta = theta
        if radius is not None:
            self.radius = radius
        else:
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
