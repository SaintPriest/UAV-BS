import math

from vpython import *


class Motion:
    def __init__(self, hexagon_length):
        self.hexagon_length = hexagon_length
        self.scene = canvas(title="3D Motion\n\n", width=800, height=400, background=vec(0, 0.6, 0.6))
        self.scene.caption = "\n"
        self.scene.camera.pos = vec(0, 450, 0.391)
        self.scene.camera.axis = scene.center - self.scene.camera.pos
        # self.ground = box(canvas=self.scene, pos=vec(0, -1, 0), size=vec(ground_length, 1, ground_width),
        #                   color=color.white)
        self.ground2 = extrusion(canvas=self.scene, path=[vec(0, 0, 0), vec(0, -1, 0)],
                                 shape=shapes.hexagon(length=400/math.sqrt(3), rotate=math.pi/6), color=color.white)
        self.uavs = []
        self.ues = []
        self.ue_num = 0

    def add_uav(self, position, height, radius):
        self.uavs.append(cone(canvas=self.scene, pos=position, axis=vec(0, height, 0),
                              radius=radius, opacity=0.4))

    def add_ue(self, position):
        self.ues.append(cylinder(canvas=self.scene, pos=position, axis=vec(0, 0.2, 0), opacity=0.7, color=color.black,
                                radius=0.8))
        self.ue_num = len(self.ues)

    def set_ue_num(self, num):
        for i in range(num, self.ue_num):
            self.ues[i].visible = False
        for i in range(self.ue_num, num):
            self.ues[i].visible = True
        self.ue_num = num


if __name__ == '__main__':
    motion = Motion(600, 200)