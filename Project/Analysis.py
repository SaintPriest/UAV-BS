from vpython import graph, gcurve, color
import math
import numpy as np


class Analysis:
    def __init__(self, uavs, ues):
        self.uavs = uavs
        self.ues = ues
        coverage_g = graph(title="<i>t</i>-<i>coverage</i> plot", width=600, height=450, x=0, y=400,
                   xtitle="<i>t</i> (s)", ytitle="<i>coverage</i> (%)", fast=False)
        self.coverage_gc = gcurve(graph=coverage_g, color=color.red)

    def add_coverage(self, x, y):
        self.coverage_gc.plot(pos=(x, y))

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


