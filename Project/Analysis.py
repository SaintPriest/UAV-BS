from vpython import graph, gcurve, color


class Analysis:
    def __init__(self):
        coverage_g = graph(title="<i>x</i>-<i>t</i> plot", width=600, height=450, x=0, y=400,
                   xtitle="<i>t</i> (s)", ytitle="<i>x</i> (cm)", fast=False)
        self.coverage_gc = gcurve(graph=coverage_g, color=color.red)

    def add_coverage(self, x, y):
        self.coverage_gc.plot(pos=(x, y))
