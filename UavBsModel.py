import math


class UavBsModel:
    def __init__(self, height, width):
        self.uavs = []
        self.ground = Ground(height, width)


class Uav:
    def __init__(self, position, height=100, theta=math.pi / 3, radius=None):
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
    def __init__(self, height, width):
        self.height = height
        self.width = width


if __name__ == '__main__':
    uav = Uav(position=(1, 2))
    print(uav.radius)
