from vpython import *

from Analysis import Analysis
from UavBsModel import UavBsModel, Uav
from Motion import Motion
import math


update_rate = 100

class UavBs:
    def __init__(self):
        global update_rate
        self.time = 0

        # config
        self.all_uav_curves = False

        # custom parameters
        ground_length = 100 * math.sqrt(3) * 2
        ground_width = ground_length
        uav_arrange = (3, 3)
        uav_distance = 100 * math.sqrt(3)
        uav_height = 100
        uav_theta = math.atan(1)
        ue_init_num = 300
        self.level_step = 10 / update_rate  # m/s
        self.raise_step = 5 / update_rate
        self.fall_step = 3 / update_rate

        # debug
        self.disable_uav_5 = False

        # states
        self.replacing = False
        self.update_replacing = self.update_replacing_strategy1  # function ptr
        self.replacing_state = 0

        # mutex
        self.sync_lock = False

        # UE number
        # three swap strategy buttons
        # 效能評估 通道模型: 使用者與無人機的關係
        # 輸入 每一台無人機與地面的使用者

        # model
        self.model = UavBsModel(ground_length, ground_width)
        for i in range(uav_arrange[0]):
            for j in range(uav_arrange[1] - (1 if (i % 2 == 0) else 0)):
                position_x_offset = uav_distance / 2 if (i % 2 == 0) else 0  # shift right
                self.model.uavs.append(
                    Uav(position=vec(position_x_offset + j * uav_distance, 0, i * uav_distance * math.sqrt(3) / 2),
                        height=uav_height, theta=uav_theta))
        self.model.set_ue_num(ue_init_num)

        # view
        self.motion = Motion(ground_length=self.model.ground.length, ground_width=self.model.ground.width)
        for uav_model in self.model.uavs:
            self.motion.add_uav(uav_model.position, uav_model.height, uav_model.radius)
        for ue in self.model.ues:
            self.motion.add_ue(position=vec(ue.x - self.model.ground.length / 2,
                                            ue.y, ue.z - self.model.ground.width / 2))
        self.motion.set_ue_num(ue_init_num)

        if self.disable_uav_5:
            self.motion.uavs[5].visible = False

        # analysis
        self.analysis = Analysis(self.model.uavs, self.model.ues, self.all_uav_curves)

        # UI
        def set_all_height(vslider):
            height_value_text.text = '{:1.1f} m'.format(vslider.value)
            for uav_model in self.model.uavs:
                uav_model.height = vslider.value
                uav_model.update_radius()
            self.update_height()

        wtext(text='UAV Height')
        height_slider = slider(min=1.0, max=1000.0, value=uav_height, length=200, bind=set_all_height, right=15,
                               step=0.1)
        height_value_text = wtext(text='{:1.1f} m\n\n'.format(height_slider.value))

        def set_all_theta(vslider):
            theta_value_text.text = '{:1.1f} degrees'.format(vslider.value)
            for uav_model in self.model.uavs:
                uav_model.theta = radians(vslider.value)
                uav_model.update_radius()
            self.update_height()

        wtext(text='UAV Theta')
        theta_slider = slider(min=1.0, max=89.0, value=degrees(uav_theta), length=200, bind=set_all_theta, right=15,
                              step=0.1)
        theta_value_text = wtext(text='{:1.1f} degrees\n\n'.format(theta_slider.value))

        def set_ue_num(num_input):
            while self.sync_lock:
                pass
            self.model.set_ue_num(int(num_input.number))
            self.motion.set_ue_num(int(num_input.number))

        wtext(text='# UEs   ')
        ue_num_input = winput(text=str(ue_init_num), bind=set_ue_num)

        def start_replacing_strategy1():
            self.replacing = True
            self.update_replacing = self.update_replacing_strategy1
            for button in self.replacement_buttons:
                button.disabled = True
        self.replacement_buttons = [button(bind=start_replacing_strategy1, text='Replace 1')]

        def start_replacing_strategy2():
            self.replacing = True
            self.update_replacing = self.update_replacing_strategy2
            for button in self.replacement_buttons:
                button.disabled = True
        self.replacement_buttons.append(button(bind=start_replacing_strategy2, text='Replace 2'))

    def update_replacing_strategy1(self):
        if not self.replacing:
            return

        if self.replacing_state == 0:  # init state
            self.model.uavs.append(
                Uav(position=vec(max(map(lambda x: x.position.x, self.model.uavs)) +
                                 (self.model.uavs[1].position.x - self.model.uavs[0].position.x) / 2,
                                 0,
                                 self.model.uavs[len(self.model.uavs) // 2].position.z),
                    height=self.model.uavs[0].height - 20,
                    theta=self.model.uavs[0].theta))
            self.motion.add_uav(self.model.uavs[-1].position, self.model.uavs[-1].height, self.model.uavs[-1].radius)
            if self.all_uav_curves:
                self.analysis.add_speed_gc()
            self.replacing_state = 1

        elif self.replacing_state == 1:  # moving state
            target_uav = self.model.uavs[(len(self.model.uavs) - 1) // 2]
            new_uav = self.model.uavs[-1]
            new_uav.position.x -= min(self.level_step, new_uav.position.x - target_uav.position.x)
            if isclose(new_uav.position.x, target_uav.position.x):
                self.replacing_state = 2

        elif self.replacing_state == 2:  # swapping state
            target_uav = self.model.uavs[(len(self.model.uavs) - 1) // 2]
            target_height = self.model.uavs[0].height
            new_uav = self.model.uavs[-1]
            dy = min(self.raise_step, target_height - new_uav.height)
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
            old_uav.position.x += min(self.level_step, target_x - old_uav.position.x)
            if isclose(old_uav.position.x, target_x):
                self.replacing_state = 4

        else:  # finalize
            self.model.uavs[(len(self.model.uavs) - 1) // 2], self.model.uavs[-1] = \
                self.model.uavs[-1], self.model.uavs[(len(self.model.uavs) - 1) // 2]
            del self.model.uavs[-1]

            self.motion.uavs[(len(self.motion.uavs) - 1) // 2], self.motion.uavs[-1] = \
                self.motion.uavs[-1], self.motion.uavs[(len(self.motion.uavs) - 1) // 2]
            self.motion.uavs[-1].visible = False
            del self.motion.uavs[-1]

            if self.all_uav_curves:
                self.analysis.speed_gc[(len(self.analysis.speed_gc) - 1) // 2], self.analysis.speed_gc[-1] = \
                    self.analysis.speed_gc[-1], self.analysis.speed_gc[(len(self.analysis.speed_gc) - 1) // 2]
                self.analysis.del_speed_gc()

            self.replacing_state = 0
            self.replacing = False

            for button in self.replacement_buttons:
                button.disabled = False

    def update_replacing_strategy2(self):
        if not self.replacing:
            return

        if self.replacing_state == 0:  # init state
            pass

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
        if self.time % 20 != 0:
            return

        coverage = 0
        self.sync_lock = True
        for ue in self.model.ues:
            for uav in self.model.uavs:
                if self.disable_uav_5:
                    if uav == self.model.uavs[5]:
                        continue
                if self.analysis.cover(ue, uav):
                    coverage += 1
                    break
        self.analysis.add_coverage(self.time / update_rate, coverage * 100 / len(self.model.ues))

        speed_sum = 0

        for j in range(len(self.model.uavs)):
            speed = self.analysis.C_(j) / (10 ** 9)
            if self.all_uav_curves:
                self.analysis.add_speed(j, self.time / update_rate, speed)
            speed_sum += speed

        self.analysis.add_total_speed(self.time / update_rate, speed_sum)
        self.sync_lock = False


if __name__ == '__main__':
    bs = UavBs()
    while True:
        rate(update_rate)
        bs.update_replacing()
        bs.update_pos()
        bs.update_analysis()
