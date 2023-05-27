from vpython import *


class Motion:
    def __init__(self, ground_height, ground_width):
        self.height = ground_height
        self.width = ground_width
        self.scene = canvas(title="3D Motion\n\n", width=800, height=400, x=0, y=0,
                            center=vec(0, 5, 0), background=vec(0, 0.6, 0.6))
        self.scene.caption = "\n"
        self.ground = box(canvas=self.scene, pos=vec(0, 0, 0), size=vec(ground_height, 1, ground_width), color=color.blue)
        self.uavs = []

    def add_uav(self, position, height, radius):
        self.uavs.append(cone(canvas=self.scene, pos=position, axis=vec(0, height, 0),
                              radius=radius, opacity=0.4))


if __name__ == '__main__':
    motion = Motion(600, 200)