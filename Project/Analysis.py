from vpython import graph, gcurve, color, vector
import math
import numpy as np


class Analysis:
    def __init__(self, uavs, ues, all_uav_curves):
        self.uavs = uavs
        self.ues = ues
        self.total_speed_g = graph(title="<i>t</i>-<i>speed</i> plot", width=600, height=450, x=0, y=400,
                                   xtitle="<i>t</i> (s)", ytitle="<i>speed</i> (Gbps)", fast=True)
        self.total_speed_gc = gcurve(graph=self.total_speed_g, color=color.red)

        if all_uav_curves:
            self.speed_g = graph(title="<i>t</i>-<i>speed</i> plot", width=600, height=450, x=0, y=400,
                               xtitle="<i>t</i> (s)", ytitle="<i>total speed</i> (Gbps)", fast=True)
            self.speed_gc = []
            colors = [color.blue, color.cyan, color.green, color.orange, color.magenta, color.purple,
                      color.yellow, color.black, vector(0.8,0.4,0.6), color.red] * 5
            for i in range(len(self.uavs)):
                self.speed_gc.append(gcurve(graph=self.speed_g, color=colors[i]))

        coverage_g = graph(title="<i>t</i>-<i>coverage</i> plot", width=600, height=450, x=0, y=400,
                           xtitle="<i>t</i> (s)", ytitle="<i>coverage</i> (%)", fast=True)
        self.coverage_gc = gcurve(graph=coverage_g, color=color.blue)

    def add_coverage(self, x, y):
        self.coverage_gc.plot(pos=(x, y))

    def add_total_speed(self, x, y):
        self.total_speed_gc.plot(pos=(x, y))

    def add_speed(self, i, x, y):
        self.speed_gc[i].plot(pos=(x, y))

    def add_speed_gc(self):
        self.speed_gc.append(gcurve(graph=self.speed_g, color=color.red))

    def del_speed_gc(self):
        del self.speed_gc[-1]

    def h_(self, j):
        return self.uavs[j].height

    def r_(self, i, j):
        return self.r(self.ues[i], self.uavs[j].position)

    def r(self, v1, v2):
        return np.linalg.norm((v1.x - v2.x, v1.z - v2.z))

    def L(self, h, r):
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

    def SINR_(self, i, j):
        P = 100
        B = 2 * (10 ** 7)
        N0 = 4.1843795 / (10 ** 21)
        return P * (10 ** (-self.L(self.h_(j), self.r_(i, j)) / 10)) / (self.I_(i, j) + B * N0)

    def I_(self, i, j):
        P = 100
        accu = 0
        for jp in range(len(self.uavs)):
            if jp != j:
                accu += P * (10 ** (-self.L(self.h_(j), self.r_(i, jp)) / 10)) * self.phi_(i, j, jp)
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
                c_acc += self.c_(i, j)
        return c_acc
