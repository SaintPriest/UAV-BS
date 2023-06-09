from vpython import graph, gcurve, color, vector as vec, canvas
import math
import numpy as np


class Analysis:
    def __init__(self, uavs, ues, all_uav_curves):
        self.uavs = uavs
        self.ues = ues
        self.total_speed_g = graph(title="<i>t</i>-<i>speed</i> plot", align='left',
                                   xtitle="<i>t</i> (s)", ytitle="<i>system-sum-rate</i> (Mbps)", fast=True)
        self.total_speed_gc = gcurve(graph=self.total_speed_g, color=color.red)

        if all_uav_curves:
            self.speed_g = graph(title="<i>t</i>-<i>speed</i> plot", align='left',
                                 xtitle="<i>t</i> (s)", ytitle="<i>total speed</i> (Mbps)", fast=True)
            self.speed_gc = []
            colors = [color.blue, color.cyan, color.green, color.orange, color.magenta, color.purple,
                      color.yellow, color.black, vec(0.8, 0.4, 0.6), color.red] * 5
            for i in range(len(self.uavs)):
                self.speed_gc.append(gcurve(graph=self.speed_g, color=colors[i]))

        coverage_g = graph(title="<i>t</i>-<i>coverage</i> plot", align='left',
                           xtitle="<i>t</i> (s)", ytitle="<i>coverage</i> (%)", fast=True)
        self.coverage_gc = gcurve(graph=coverage_g, color=color.blue)

    def clear_curves(self):
        self.coverage_gc.data = []
        self.total_speed_gc.data = []
        for curve in self.speed_gc:
            curve.data = []

    def add_coverage(self, x, y):
        self.coverage_gc.plot(pos=(x, y))

    def add_total_speed(self, x, y):
        self.total_speed_gc.plot(pos=(x, y))

    def add_speed(self, i, x, y):
        self.speed_gc[i].plot(pos=(x, y))

    def add_speed_gc(self):
        self.speed_gc.append(gcurve(graph=self.speed_g, color=color.red))

    def del_speed_gc(self):
        self.speed_gc[-1].data = []
        del self.speed_gc[-1]

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

    # def L(self, h, r):
    #     a = 12.08
    #     b = 0.11
    #     fc = 2 * (10 ** 9)
    #     c = 3 * (10 ** 8)
    #     eta_los = 1.6
    #     eta_nlos = 23
    #
    #     theta = math.atan(h / r)
    #
    #     l_part1 = (eta_los - eta_nlos) / (1 + a * math.exp(-b * (180 / math.pi * theta - a)))
    #     l_part2 = 20 * math.log(r * (1 / math.cos(theta)), 10)
    #     l_part3 = 20 * math.log(4 * math.pi * fc / c, 10)
    #     return l_part1 + l_part2 + l_part3 + eta_nlos

    def orig_L(self, h, r, d):
        p_los = self.P_los(h, r, d)
        l_los = self.L_los(d)
        p_nlos = 1 - p_los
        l_nlos = self.L_nlos(d)
        l = p_los * l_los + p_nlos * l_nlos
        # print(l, p_los, l_los, p_nlos, l_nlos)
        # print(l - self.L(self, h, r))
        return l

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
        rtn = P * (10 ** (-self.orig_L(self.h_(j), self.r_(i, j), self.d_(i, j)) / 10)) / (self.I_(i, j) + B * N0)
        # print('SINR', rtn)
        return rtn

    def I_(self, i, j):
        P = 100
        accu = 0
        for jp in range(len(self.uavs)):
            if jp != j:
                accu += P * (10 ** (-self.orig_L(self.h_(jp), self.r_(i, jp), self.d_(i, jp)) / 10)) * self.phi_(i, j, jp)
        return accu

    def phi_(self, i, j, jp):
        if self.cover(self.ues[i], self.uavs[j]) and self.cover(self.ues[i], self.uavs[jp]):
            return 1
        return 0

    def cover(self, ue, uav):
        return self.r(uav.position, ue) <= uav.radius

    def c_(self, i, j):
        B = 2 * (10 ** 7)
        return B * math.log(1 + self.SINR_(i, j), 2)

    def C_(self, j):
        c_acc = 0
        for i in range(len(self.ues)):
            if self.cover(self.ues[i], self.uavs[j]):
                _c = self.c_(i, j)
                c_acc += _c
                # print(f'UE ({self.ues[i].x}, {self.ues[i].z}), UAV({self.uavs[j].position.x}, {self.uavs[j].position.z}, h={self.uavs[j].height}, r={self.uavs[j].radius}), speed = {_c}')

        return c_acc
