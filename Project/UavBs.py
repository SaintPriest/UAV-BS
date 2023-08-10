from vpython import *

from Analysis import Analysis
from UavBsModel import UavBsModel, Uav
from Motion import Motion
import math
import csv

# system config
sys_config_update_rate = 100  # system updates 100 times per second, i.e., update once per 0.01 second.


class UavBs:
    def __init__(self):
        global sys_config_update_rate
        self.time = 0

        # config
        is_all_uav_curves_enabled = True  # high cost
        is_ground_coverage_enabled = True  # high cost

        # custom parameters
        hexagon_length = 400 / math.sqrt(3)
        uav_arrange = (3, 3)
        self.uav_distance = 100 * math.sqrt(3)
        uav_height = 100
        uav_theta = math.atan(1)
        ue_init_num = 300
        uav_speed_up = 5  # speed up of UAV
        self.level_step = 10 * uav_speed_up / sys_config_update_rate  # m/s
        self.raise_step = 5 * uav_speed_up / sys_config_update_rate
        self.fall_step = 3 * uav_speed_up / sys_config_update_rate

        # states
        self.replacing = False
        self.reproducing = False
        self.update_replacing_strategy = None  # function ptr
        self.replacing_state = 0
        self.REPLACING_STATE_WAIT_LAST_ANALYSIS = 254 #### change to self.wait_analysis = True
        self.REPLACING_STATE_FINALIZE = 255
        analyze_update_rate = 5  # figures updates 5 times per second. It should be a factor of sys_config_update_rate
        self.analyze_update_period = sys_config_update_rate // analyze_update_rate
        fast_analyze = False  # Turn it off if you need analysis data

        # mutex
        self.sync_lock = False

        # function static variables for replacing
        self.replacing_time_start = 0
        self.replacing_inited = False

        # replacing strategy 1
        self.has_additional_uav = False

        # replacing strategy 2
        self.orig_center_uav_x = 0
        self.orig_center_uav_y = 0
        self.orig_near_uav_x = 0
        self.orig_near_uav_y = 0
        self.replacing_strategy2_circle_x = 0
        self.replacing_strategy2_circle_y = 0
        self.update_replacing_strategy2_theta = 0
        self.update_replacing_strategy2_count = 0
        self.replacing_y_weight = 0.5  # orig: 1

        # model
        uavs = []
        for i in range(uav_arrange[0]):
            for j in range(uav_arrange[1] - (1 if (i % 2 == 0) else 0)):
                position_x_offset = self.uav_distance / 2 if (i % 2 == 0) else 0  # shift right
                uavs.append(
                    Uav(position=vec(position_x_offset + j * self.uav_distance,
                                     0,
                                     i * self.uav_distance * math.sqrt(3) / 2),
                        height=uav_height, theta=uav_theta))
        self.model = UavBsModel(hexagon_length, uavs)

        # analysis
        self.analysis = Analysis(self.model.uavs, self.model.ues, self.model.ues_backup,
                                 is_all_uav_curves_enabled, is_ground_coverage_enabled,
                                 fast_analyze)

        # view
        self.motion = Motion(hexagon_length)
        for uav_model in self.model.uavs:
            self.motion.add_uav(uav_model.position, uav_model.height, uav_model.radius)
        for ue in self.model.ues:
            self.motion.add_ue(position=vec(ue.x - self.model.center.x,
                                            ue.y, ue.z - self.model.center.z))

        self.model.set_ue_num(ue_init_num)
        self.motion.set_ue_num(ue_init_num)

        # UI
        def set_all_height(vslider):
            height_value_text.text = '{:1.1f} m\n\n'.format(vslider.value)
            for uav_model in self.model.uavs:
                uav_model.height = vslider.value
                uav_model.update_radius()
            self.update_height()

        wtext(text='UAV Height')
        height_slider = slider(min=10.0, max=100.0, value=uav_height, length=200, bind=set_all_height, right=15,
                               step=0.1)
        height_value_text = wtext(text='{:1.1f} m\n\n'.format(height_slider.value))

        def set_all_theta(vslider):
            theta_value_text.text = '{:1.1f} degrees\n\n'.format(vslider.value)
            for uav_model in self.model.uavs:
                uav_model.theta = radians(vslider.value)
                uav_model.update_radius()
            self.update_height()

        wtext(text='UAV Theta')
        theta_slider = slider(min=10.0, max=80.0, value=degrees(uav_theta), length=200, bind=set_all_theta, right=15,
                              step=0.1)
        theta_value_text = wtext(text='{:1.1f} degrees\n\n'.format(theta_slider.value))

        def set_ue_num(num_input):
            while self.sync_lock:
                pass
            self.model.set_ue_num(int(num_input.number))
            self.motion.set_ue_num(int(num_input.number))

        wtext(text='# UEs ')
        ue_num_input = winput(text=str(ue_init_num), bind=set_ue_num)
        wtext(text='\n\n')
        self.replacement_buttons = []

        def start_replacing_strategy1():
            self.update_replacing_strategy = self.update_replacing_strategy1
            self.replacing = True

        self.replacement_buttons.append(button(bind=start_replacing_strategy1, text='Replace 1'))

        def start_replacing_strategy2():
            self.update_replacing_strategy = self.update_replacing_strategy2
            self.replacing = True

        self.replacement_buttons.append(button(bind=start_replacing_strategy2, text='Replace 2'))

        def start_reproduce_replacement():
            # copy
            self.analysis.copy_all_curves()
            self.reproducing = True
            self.replacing = True

        self.replacement_buttons.append(button(bind=start_reproduce_replacement, text='Reproduce', disabled=True))

        def export_data(button):
            button.disabled = True
            # data processing
            data_list = []
            for (time, speed_sum), (_, coverage), (_, outage) in zip(self.analysis.total_speed_curve.data,
                                                    self.analysis.ground_coverage_curve.data,
                                                    self.analysis.disconnected_rate_curve.data):
                data_list.append([time, speed_sum, coverage, outage])

            # output
            with open('data.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Time", "System sum rate (Mbps)", "Coverage (%)", "Outage rate (%)"])
                for data in data_list:
                    writer.writerow(data)
            button.disabled = False

        wtext(text=' ')
        self.replacement_buttons.append(button(bind=export_data, text='Export', disabled=True))

        wtext(text='  Replacing time ')
        self.replacing_time_text = wtext(text='0')
        wtext(text='\n\n')

    def update_replacing(self):
        if not self.replacing:
            return

        # init for replacing
        if not self.replacing_inited:
            for b in self.replacement_buttons:
                b.disabled = True

            self.replacing_state = 0
            self.replacing_time_start = self.time
            self.analysis.clear_data()
            if self.has_additional_uav:
                if self.analysis.is_all_uav_speed_curves_enabled:
                    self.analysis.del_speed_gc()
                self.has_additional_uav = False
            self.replacing_inited = True

        # UI updates
        if (self.time - self.replacing_time_start) % 10 == 0:
            self.replacing_time_text.text = f'{(self.time - self.replacing_time_start) / sys_config_update_rate} s'

        self.update_replacing_strategy()

        # callback
        if not self.replacing:
            self.replacing_inited = False
            self.reproducing = False
            self.replacing_time_text.text = f'{(self.time - self.replacing_time_start) / sys_config_update_rate} s'
            self.replacing_time_text.text += f'  |  Avg system sum rate: <b>{round(self.analysis.avg_speed(), 1)} Mbps</b>'
            self.replacing_time_text.text += f'  |  Avg coverage: <b>{round(self.analysis.avg_coverage(), 2)} %</b>'
            self.replacing_time_text.text += f'  |  Avg outage rate: <b>{round(self.analysis.avg_disconnected_rate(), 2)} %</b>'

    def update_replacing_strategy1(self):
        if self.replacing_state == 0:  # init state
            while self.sync_lock:
                pass
            self.model.uavs.append(
                Uav(position=vec(self.model.uavs[len(self.model.uavs) // 2 + 1].position.x + self.uav_distance * 0.85, 0,
                                 self.model.uavs[len(self.model.uavs) // 2].position.z),
                    height=self.model.uavs[0].height - 20,
                    theta=self.model.uavs[0].theta))
            self.motion.add_uav(self.model.uavs[-1].position, self.model.uavs[-1].height, self.model.uavs[-1].radius)
            self.has_additional_uav = True
            if self.analysis.is_all_uav_speed_curves_enabled:
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
            target_x = self.model.uavs[(len(self.model.uavs) - 1) // 2 + 1].position.x + self.uav_distance * 1.05
            old_uav = self.model.uavs[(len(self.model.uavs) - 1) // 2]
            old_uav.position.x += min(self.level_step, target_x - old_uav.position.x)
            if isclose(old_uav.position.x, target_x):
                self.replacing_state = self.REPLACING_STATE_WAIT_LAST_ANALYSIS

        elif self.replacing_state == self.REPLACING_STATE_FINALIZE:  # finalize
            orig_center_index = (len(self.model.uavs) - 1) // 2
            self.model.uavs[orig_center_index], self.model.uavs[-1] = \
                self.model.uavs[-1], self.model.uavs[orig_center_index]

            self.motion.uavs[orig_center_index], self.motion.uavs[-1] = \
                self.motion.uavs[-1], self.motion.uavs[orig_center_index]

            del self.model.uavs[-1]
            self.motion.uavs[-1].visible = False
            del self.motion.uavs[-1]

            self.replacing = False

            for button in self.replacement_buttons:
                button.disabled = False

    def update_replacing_strategy2(self):
        if self.replacing_state == 0:  # init state
            while self.sync_lock:
                pass
            # create new UAV
            self.model.uavs.append(
                Uav(position=vec(self.model.uavs[len(self.model.uavs) // 2 + 1].position.x + self.uav_distance, 0,
                                 self.model.uavs[len(self.model.uavs) // 2].position.z),
                    height=self.model.uavs[0].height,
                    theta=self.model.uavs[0].theta))
            self.motion.add_uav(self.model.uavs[-1].position, self.model.uavs[-1].height, self.model.uavs[-1].radius)
            self.has_additional_uav = True
            if self.analysis.is_all_uav_speed_curves_enabled:
                self.analysis.add_speed_gc()

            orig_center_index = (len(self.model.uavs) - 1) // 2
            self.orig_center_uav_x = self.model.uavs[orig_center_index].position.x
            self.orig_center_uav_y = self.model.uavs[orig_center_index].position.z
            self.orig_near_uav_x = self.model.uavs[orig_center_index + 1].position.x
            self.orig_near_uav_y = self.model.uavs[orig_center_index + 1].position.z
            self.replacing_strategy2_circle_x = self.model.uavs[orig_center_index].position.x + (self.uav_distance / 2)
            self.replacing_strategy2_circle_y = self.model.uavs[orig_center_index].position.z
            self.update_replacing_strategy2_theta = math.acos(
                1 - ((self.level_step ** 2) / (2 * ((self.uav_distance / 2) ** 2))))
            self.update_replacing_strategy2_count = 1
            self.replacing_state = 1

        elif self.replacing_state == 1:  # swap
            orig_center_index = (len(self.model.uavs) - 1) // 2
            center_uav = self.model.uavs[orig_center_index]
            near_uav = self.model.uavs[orig_center_index + 1]
            circle_r = self.uav_distance / 2
            theta = self.update_replacing_strategy2_theta * self.update_replacing_strategy2_count
            theta = min(math.pi, theta)
            center_uav.position.x = self.replacing_strategy2_circle_x + circle_r * math.cos(theta + math.pi)
            center_uav.position.z = self.replacing_strategy2_circle_y + circle_r * math.sin(theta + math.pi) * self.replacing_y_weight
            near_uav.position.x = self.replacing_strategy2_circle_x + circle_r * math.cos(theta)
            near_uav.position.z = self.replacing_strategy2_circle_y + circle_r * math.sin(theta) * self.replacing_y_weight

            self.update_replacing_strategy2_count += 1

            if theta == math.pi:
                center_uav.position.x = self.orig_near_uav_x
                center_uav.position.z = self.orig_near_uav_y
                near_uav.position.x = self.orig_center_uav_x
                near_uav.position.z = self.orig_center_uav_y
                self.replacing_state = 2

        elif self.replacing_state == 2:
            # initialize swapping value
            orig_center_index = (len(self.model.uavs) - 1) // 2
            self.orig_center_uav_x = self.model.uavs[orig_center_index].position.x
            self.orig_center_uav_y = self.model.uavs[orig_center_index].position.z
            self.orig_near_uav_x = self.model.uavs[-1].position.x
            self.orig_near_uav_y = self.model.uavs[-1].position.z
            self.replacing_strategy2_circle_x = self.model.uavs[orig_center_index].position.x + (self.uav_distance / 2)
            self.replacing_strategy2_circle_y = self.model.uavs[orig_center_index].position.z
            self.update_replacing_strategy2_theta = math.acos(
                1 - ((self.level_step ** 2) / (2 * ((self.uav_distance / 2) ** 2))))
            self.update_replacing_strategy2_count = 1
            self.replacing_state = 3

        elif self.replacing_state == 3:  # swap with new UAV
            orig_center_index = (len(self.model.uavs) - 1) // 2
            center_uav = self.model.uavs[orig_center_index]
            near_uav = self.model.uavs[-1]
            circle_r = self.uav_distance / 2
            theta = self.update_replacing_strategy2_theta * self.update_replacing_strategy2_count
            theta = min(math.pi, theta)
            center_uav.position.x = self.replacing_strategy2_circle_x + circle_r * math.cos(theta + math.pi)
            center_uav.position.z = self.replacing_strategy2_circle_y + circle_r * math.sin(theta + math.pi) * self.replacing_y_weight
            near_uav.position.x = self.replacing_strategy2_circle_x + circle_r * math.cos(theta)
            near_uav.position.z = self.replacing_strategy2_circle_y + circle_r * math.sin(theta) * self.replacing_y_weight

            self.update_replacing_strategy2_count += 1

            if theta == math.pi:
                center_uav.position.x = self.orig_near_uav_x
                center_uav.position.z = self.orig_near_uav_y
                near_uav.position.x = self.orig_center_uav_x
                near_uav.position.z = self.orig_center_uav_y
                self.replacing_state = self.REPLACING_STATE_WAIT_LAST_ANALYSIS

        elif self.replacing_state == self.REPLACING_STATE_FINALIZE:  # finalize
            orig_center_index = (len(self.model.uavs) - 1) // 2
            near_index = orig_center_index + 1
            self.model.uavs[orig_center_index], self.model.uavs[near_index] = \
                self.model.uavs[near_index], self.model.uavs[orig_center_index]
            self.motion.uavs[orig_center_index], self.motion.uavs[near_index] = \
                self.motion.uavs[near_index], self.motion.uavs[orig_center_index]

            orig_center_index = near_index
            near_index = -1
            self.model.uavs[orig_center_index], self.model.uavs[near_index] = \
                self.model.uavs[near_index], self.model.uavs[orig_center_index]
            self.motion.uavs[orig_center_index], self.motion.uavs[near_index] = \
                self.motion.uavs[near_index], self.motion.uavs[orig_center_index]

            del self.model.uavs[-1]
            self.motion.uavs[-1].visible = False
            del self.motion.uavs[-1]

            self.replacing = False

            for button in self.replacement_buttons:
                button.disabled = False

    def update_pos(self):
        for uav, uav_model in zip(self.motion.uavs, self.model.uavs):
            uav.pos = vec(uav_model.position.x - self.model.center.x,
                          uav_model.position.y,
                          uav_model.position.z - self.model.center.z)

    def update_height(self):
        for uav, uav_model in zip(self.motion.uavs, self.model.uavs):
            uav.axis = vec(0, uav_model.height, 0)
            uav.radius = uav_model.radius

    def update_analysis(self):
        if not self.replacing:
            return

        analyze_time = self.time - self.replacing_time_start
        if analyze_time % self.analyze_update_period != 0:
            return
        analyze_time = analyze_time / sys_config_update_rate

        self.sync_lock = True

        if not self.reproducing:
            self.analysis.update_cover_map()
            self.analysis.add_disconnected_rate(analyze_time, round((1 - self.analysis.connected_rate) * 100, 2))
            if self.analysis.is_ground_coverage_enabled:
                self.analysis.add_ground_coverage(analyze_time, round(self.analysis.ground_coverage * 100, 2))

            speed_sum = 0
            for j in range(len(self.model.uavs)):
                speed = self.analysis.C_(j) / (10 ** 6)
                if self.analysis.is_all_uav_speed_curves_enabled:
                    self.analysis.add_speed(j, analyze_time, round(speed, 1))
                speed_sum += speed

            self.analysis.add_total_speed(analyze_time, round(speed_sum, 1))

        else:
            index = len(self.analysis.disconnected_rate_curve.data)
            assert analyze_time == self.analysis.disconnected_rate_curve_data_copy[index][0]

            self.analysis.add_disconnected_rate(analyze_time, self.analysis.disconnected_rate_curve_data_copy[index][1])

            if self.analysis.is_ground_coverage_enabled:
                self.analysis.add_ground_coverage(analyze_time, self.analysis.ground_coverage_curve_data_copy[index][1])

            if self.analysis.is_all_uav_speed_curves_enabled:
                for j in range(len(self.model.uavs)):
                    self.analysis.add_speed(j, analyze_time, self.analysis.all_speed_curve_data_array_copy[j][index][1])

            self.analysis.add_total_speed(analyze_time, self.analysis.total_speed_curve_data_copy[index][1])

        self.sync_lock = False
        if self.replacing_state == self.REPLACING_STATE_WAIT_LAST_ANALYSIS:
            self.replacing_state = self.REPLACING_STATE_FINALIZE

    def update(self):
        self.update_replacing()
        self.update_pos()
        self.update_analysis()
        self.time += 1


def main():
    bs = UavBs()
    while True:
        rate(sys_config_update_rate)
        bs.update()


if __name__ == '__main__':
    main()
