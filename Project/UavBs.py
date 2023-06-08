from vpython import *

from Analysis import Analysis
from UavBsModel import UavBsModel, Uav
from Motion import Motion
import math
import numpy as np;


class UavBs:
    def __init__(self):
        self.time = 0

        # custom parameters
        ground_length = 100 * math.sqrt(3) * 2 + 100
        ground_width = 300
        uav_arrange = (3, 3)
        uav_distance = 100 * math.sqrt(3)
        uav_height = 120
        uav_theta = math.atan(1.2)

        # debug
        self.disable_uav_5 = True

        # states
        self.replacing = False
        self.update_replacing = self.update_replacing_strategy1  # function ptr
        self.replacing_state = 0

        # UE number
        # three swap strategy buttons
        # 效能評估 通道模型: 使用者與無人機的關係
        # 輸入 每一台無人機與地面的使用者

        # model
        self.model = UavBsModel(ground_length, ground_width)
        for i in range(uav_arrange[0]):
            for j in range(uav_arrange[1]):
                position_x_offset = uav_distance / 2 if (i % 2 == 1) else 0  # shift right
                self.model.uavs.append(
                    Uav(position=vec(position_x_offset + j * uav_distance, 0, i * uav_distance * math.sqrt(3) / 2),
                        height=uav_height, theta=uav_theta))

        # view
        self.motion = Motion(ground_length=self.model.ground.length, ground_width=self.model.ground.width)
        for uav_model in self.model.uavs:
            self.motion.add_uav(uav_model.position, uav_model.height, uav_model.radius)
        for ue_x, ue_y in zip(self.model.ue_x, self.model.ue_y):
            self.motion.add_ue(position=vec(ue_x, 1, ue_y))

        if self.disable_uav_5:
            self.motion.uavs[5].visible = False

        # analysis
        self.analysis = Analysis()

        # UI
        def set_all_height(vslider):
            height_value_text.text = '{:1.1f} m'.format(vslider.value)
            for uav_model in self.model.uavs:
                uav_model.height = vslider.value
                uav_model.update_radius()
            self.update_height()

        height_value_text = wtext(text='UAV Height')
        height_slider = slider(min=0.0, max=1000.0, value=uav_height, length=200, bind=set_all_height, right=15)
        height_value_text = wtext(text='{:1.1f} m\n\n'.format(height_slider.value))

        def set_all_theta(vslider):
            theta_value_text.text = '{:1.1f} degrees'.format(vslider.value)
            for uav_model in self.model.uavs:
                uav_model.theta = radians(vslider.value)
                uav_model.update_radius()
            self.update_height()

        theta_value_text = wtext(text='UAV Theta')
        theta_slider = slider(min=1.0, max=89.0, value=degrees(uav_theta), length=200, bind=set_all_theta, right=15)
        theta_value_text = wtext(text='{:1.1f} degrees\n\n'.format(theta_slider.value))

        def start_replacing_strategy1():
            self.replacing = True
            self.update_replacing = self.update_replacing_strategy1

        replacement1_button = button(bind=start_replacing_strategy1, text='Replace 1')

    def update_replacing_strategy1(self):
        if not self.replacing:
            return

        if self.replacing_state == 0:  # init state
            self.model.uavs.append(
                Uav(position=vec(max(map(lambda x: x.position.x, self.model.uavs)) + 2 * (
                        self.model.uavs[1].position.x - self.model.uavs[0].position.x),
                                 0,
                                 self.model.uavs[len(self.model.uavs) // 2].position.z),
                    height=self.model.uavs[0].height - 20,
                    theta=self.model.uavs[0].theta))
            self.motion.add_uav(self.model.uavs[-1].position, self.model.uavs[-1].height, self.model.uavs[-1].radius)
            self.replacing_state = 1

        elif self.replacing_state == 1:  # moving state
            target_uav = self.model.uavs[(len(self.model.uavs) - 1) // 2]
            new_uav = self.model.uavs[-1]
            new_uav.position.x -= min(0.25, new_uav.position.x - target_uav.position.x)
            if isclose(new_uav.position.x, target_uav.position.x):
                self.replacing_state = 2

        elif self.replacing_state == 2:  # swapping state
            target_uav = self.model.uavs[(len(self.model.uavs) - 1) // 2]
            target_height = self.model.uavs[0].height
            new_uav = self.model.uavs[-1]
            dy = min(0.1, target_height - new_uav.height)
            new_uav.height += dy
            new_uav.update_radius()
            target_uav.height += dy
            target_uav.update_radius()
            self.update_height()
            if isclose(new_uav.height, target_height):
                self.replacing_state = 3

        elif self.replacing_state == 3:
            target_x = max(map(lambda x: x.position.x, self.model.uavs[(len(self.model.uavs) - 1) // 2 + 1:])) + \
                       self.model.uavs[1].position.x - self.model.uavs[0].position.x
            old_uav = self.model.uavs[(len(self.model.uavs) - 1) // 2]
            old_uav.position.x += min(0.25, target_x - old_uav.position.x)
            if isclose(old_uav.position.x, target_x):
                self.replacing_state = 4

        else:  # finalize
            self.model.uavs[(len(self.model.uavs) - 1) // 2], self.model.uavs[-1] = self.model.uavs[-1], \
                self.model.uavs[(len(self.model.uavs) - 1) // 2]
            self.motion.uavs[(len(self.motion.uavs) - 1) // 2], self.motion.uavs[-1] = self.motion.uavs[-1], \
                self.motion.uavs[(len(self.motion.uavs) - 1) // 2]
            del self.model.uavs[-1]
            self.motion.uavs[-1].visible = False
            del self.motion.uavs[-1]
            self.replacing_state = 0
            self.replacing = False

    def update_pos(self):
        for uav, uav_model in zip(self.motion.uavs, self.model.uavs):
            uav.pos = vec(uav_model.position.x - self.model.ground.length // 2,
                          uav_model.position.y,
                          uav_model.position.z - self.model.ground.width // 2)

    def update_height(self):
        for uav, uav_model in zip(self.motion.uavs, self.model.uavs):
            uav.axis = vec(0, uav_model.height, 0)
            uav.radius = uav_model.radius

    def update_analysis(self):
        self.time += 1
        coverage = 0
        if self.time % 40 != 0:
            return

        for ue_x, ue_y in zip(self.model.ue_x, self.model.ue_y):
            x = ue_x + (self.model.ground.length / 2)
            y = ue_y + (self.model.ground.width / 2)
            for uav in self.model.uavs:
                if self.disable_uav_5:
                    if uav == self.model.uavs[5]:
                        continue
                if np.linalg.norm((uav.position.x - x, uav.position.z - y)) <= uav.radius:
                    coverage += 1
                    break
        self.analysis.add_coverage(self.time / 1000, coverage / len(self.model.ue_x))


if __name__ == '__main__':
    bs = UavBs()
    while True:
        rate(1000)
        bs.update_replacing()
        bs.update_pos()
        bs.update_analysis()
