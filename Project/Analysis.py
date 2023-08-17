import copy
from vpython import graph, gcurve, color, vector as vec
import math
import numpy as np


class Analysis:
    def __init__(self, uavs, ues, ues_backup, max_data_rate, is_all_uav_speed_curves_enabled, is_ground_coverage_enabled, fast):
        self.uavs = uavs
        self.ues = ues
        self.ues_backup = ues_backup
        self.max_data_rate = max_data_rate
        self.is_all_uav_speed_curves_enabled = is_all_uav_speed_curves_enabled
        self.is_ground_coverage_enabled = is_ground_coverage_enabled
        self.cover_map = np.zeros((len(ues) if not is_ground_coverage_enabled else len(ues_backup),
                                   len(uavs) + 2))
        self.connected_rate = 0
        self.ground_coverage = 0
        self.total_speed_g = graph(title="<i>t</i> - <i>system sum rate</i> plot", align='left',
                                   xtitle="<i>t</i> (s)", ytitle="<i>system-sum-rate</i> (Mbps)", fast=fast)
        self.total_speed_curve = gcurve(graph=self.total_speed_g, color=color.red)

        if self.is_all_uav_speed_curves_enabled:
            self.speed_g = graph(title="<i>t</i> - <i>system rate</i> plot", align='left',
                                 xtitle="<i>t</i> (s)", ytitle="<i>rate</i> (Mbps)", fast=fast)
            self.all_speed_curve = []
            colors = [color.blue, color.green, color.orange, color.magenta, color.purple,
                      color.yellow, color.black, vec(0.2, 0.55, 0.6)] * 5
            for i in range(len(self.uavs)):
                self.all_speed_curve.append(gcurve(graph=self.speed_g, color=colors[i]))

        disconnected_rate_g = graph(title="<i>t</i> - <i>outage rate</i> plot", align='left',
                           xtitle="<i>t</i> (s)", ytitle="<i>outage rate</i> (%)", fast=fast)
        self.disconnected_rate_curve = gcurve(graph=disconnected_rate_g, color=color.blue)

        if self.is_ground_coverage_enabled:
            ground_coverage_g = graph(title="<i>t</i> - <i>coverage</i> plot", align='left',
                               xtitle="<i>t</i> (s)", ytitle="<i>coverage</i> (%)", fast=fast)
            self.ground_coverage_curve = gcurve(graph=ground_coverage_g, color=color.orange)

        self.total_speed_curve_data_copy = []
        self.all_speed_curve_data_array_copy = []
        self.disconnected_rate_curve_data_copy = []
        self.ground_coverage_curve_data_copy = []

    def update_cover_map(self):
        connected_num = 0
        if self.is_ground_coverage_enabled:
            theoretical_connected_num = 0
            for i, ue in enumerate(self.ues_backup):
                self.cover_map[i][-1] = 0
                for j, uav in enumerate(self.uavs):
                    self.cover_map[i][j] = uav.opened and self.cover(ue, uav)
                    self.cover_map[i][-1] = self.cover_map[i][-1] or self.cover_map[i][j]
                if self.cover_map[i][-1]:
                    theoretical_connected_num += 1
                    if i < len(self.ues):
                        connected_num += 1

            self.connected_rate = connected_num / len(self.ues)
            self.ground_coverage = theoretical_connected_num / len(self.ues_backup)

        else:
            for i, ue in enumerate(self.ues):
                self.cover_map[i][-1] = 0
                for j, uav in enumerate(self.uavs):
                    self.cover_map[i][j] = uav.opened and self.cover(ue, uav)
                    self.cover_map[i][-1] = self.cover_map[i][-1] or self.cover_map[i][j]
                if self.cover_map[i][-1]:
                    connected_num += 1
            self.connected_rate = connected_num / len(self.ues)

    def is_connected(self, i):
        return self.cover_map[i][-1]

    def avg_coverage(self):
        c_sum = 0
        for t, c in self.ground_coverage_curve.data:
            c_sum += c
        return c_sum / len(self.disconnected_rate_curve.data)

    def avg_disconnected_rate(self):
        r_sum = 0
        for t, r in self.disconnected_rate_curve.data:
            r_sum += r
        return r_sum / len(self.disconnected_rate_curve.data)

    def avg_speed(self):
        s_sum = 0
        for t, s in self.total_speed_curve.data:
            s_sum += s
        return s_sum / len(self.total_speed_curve.data)

    def clear_data(self):
        self.disconnected_rate_curve.data = []
        if self.is_ground_coverage_enabled:
            self.ground_coverage_curve.data = []
        self.total_speed_curve.data = []
        if self.is_all_uav_speed_curves_enabled:
            for curve in self.all_speed_curve:
                curve.data = []

    def add_disconnected_rate(self, x, y):
        self.disconnected_rate_curve.plot(pos=(x, y))

    def add_ground_coverage(self, x, y):
        self.ground_coverage_curve.plot(pos=(x, y))

    def add_total_speed(self, x, y):
        self.total_speed_curve.plot(pos=(x, y))

    def add_speed(self, i, x, y):
        self.all_speed_curve[i].plot(pos=(x, y))

    def add_speed_gc(self):
        self.all_speed_curve.append(gcurve(graph=self.speed_g, color=color.red))

    def del_speed_gc(self):
        self.all_speed_curve[-1].data = []
        del self.all_speed_curve[-1]

    def h_(self, j):
        return self.uavs[j].height

    def r_(self, i, j):
        return self.r(self.ues[i], self.uavs[j].position)

    def r(self, v1, v2):
        return np.linalg.norm((v1.x - v2.x, v1.z - v2.z))

    def d_(self, i, j):
        u = self.uavs[j].position
        e = self.ues[i]
        return np.linalg.norm((u.x - e.x, u.z - e.z, self.h_(j)))

    def L(self, h, r, d):
        a = 12.08
        b = 0.11
        fc = 2 * (10 ** 9)
        c = 3 * (10 ** 8)
        eta_los = 1.6
        eta_nlos = 23

        theta = math.atan(h / r)

        l_part1 = (eta_los - eta_nlos) / (1 + a * math.exp(-b * (180 / math.pi * theta - a)))
        l_part2 = 20 * math.log(r * (1 / math.cos(theta)), 10)
        l_part3 = 20 * math.log(4 * math.pi * fc / c, 10)
        return l_part1 + l_part2 + l_part3 + eta_nlos

    # def orig_L(self, h, r, d):
    #     p_los = self.P_los(h, r, d)
    #     l_los = self.L_los(d)
    #     p_nlos = 1 - p_los
    #     l_nlos = self.L_nlos(d)
    #     l = p_los * l_los + p_nlos * l_nlos
    #     # print(l, p_los, l_los, p_nlos, l_nlos)
    #     # print(l - self.L(self, h, r))
    #     return l

    def P_los(self, h, r, d):
        a = 12.08
        b = 0.11
        return 1 / (1 + a * math.exp(-b * (180 / math.pi * math.asin(h / d) - a)))

    def L_los(self, d):
        fc = 2 * (10 ** 9)
        c = 3 * (10 ** 8)
        eta_los = 1.6
        return 20 * math.log(4 * math.pi * fc * d / c, 10) + eta_los

    def L_nlos(self, d):
        fc = 2 * (10 ** 9)
        c = 3 * (10 ** 8)
        eta_nlos = 23
        return 20 * math.log(4 * math.pi * fc * d / c, 10) + eta_nlos

    def SINR_(self, i, j):
        P = 100
        B = 2 * (10 ** 7)
        N0 = 4.1843795 * (10 ** -21)
        rtn = P * (10 ** (-self.L(self.h_(j), self.r_(i, j), self.d_(i, j)) / 10)) / (self.I_(i, j) + B * N0)
        # print('SINR', rtn)
        return rtn

    def I_(self, i, j):
        P = 100
        accu = 0
        for jp in range(len(self.uavs)):
            if jp != j:
                accu += P * (10 ** (-self.L(self.h_(jp), self.r_(i, jp), self.d_(i, jp)) / 10)) * self.phi_(i, j, jp)
        return accu

    def phi_(self, i, j, jp):
        if self.cover_(i, j) and self.cover_(i, jp):
            return 1
        return 0

    def cover_(self, i, j):
        return self.cover_map[i][j]

    def cover(self, ue, uav):
        return self.r(uav.position, ue) <= uav.radius

    def c_(self, i, j):
        B = 2 * (10 ** 7)
        return min(self.max_data_rate, B * math.log(1 + self.SINR_(i, j), 2))

    def C_(self, j):
        if not self.uavs[j].opened:
            return 0
        c_acc = 0
        for i in range(len(self.ues)):
            if self.cover_(i, j):
                _c = self.c_(i, j)
                c_acc += _c
                # print(f'UE ({self.ues[i].x}, {self.ues[i].z}), UAV({self.uavs[j].position.x}, {self.uavs[j].position.z}, h={self.uavs[j].height}, r={self.uavs[j].radius}), speed = {_c}')
        return min(self.max_data_rate, c_acc)

    def copy_all_curves(self):
        self.total_speed_curve_data_copy = copy.deepcopy(self.total_speed_curve.data)

        if self.is_all_uav_speed_curves_enabled:
            self.all_speed_curve_data_array_copy = []
            for data in map(lambda x: x.data, self.all_speed_curve):
                self.all_speed_curve_data_array_copy.append(copy.deepcopy(data))

        self.disconnected_rate_curve_data_copy = copy.deepcopy(self.disconnected_rate_curve.data)

        if self.is_ground_coverage_enabled:
            self.ground_coverage_curve_data_copy = copy.deepcopy(self.ground_coverage_curve.data)
