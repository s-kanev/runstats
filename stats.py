#!/bin/python

from xml.dom.minidom import parse

class Lap():
    def __init__(self, dist, time): 
        self.dist = dist
        self.time = time
        self.points = []

    def __str__(self):
        return ("%f %f" % (self.dist, self.time))
    def __repr__(self):
        return ("%f %f" % (self.dist, self.time))

if __name__ == "__main__":
    doc = parse("/home/skanev/.antd/0xe42063aa/tcx/20121021-120107.tcx")

    new_laps = []
    laps = doc.getElementsByTagName("Lap")
    for lap in laps:
        for dist in lap.getElementsByTagName("DistanceMeters"):
            if dist.parentNode == lap:
                dist_val = float(dist.firstChild.data)
                break
        for dist in lap.getElementsByTagName("TotalTimeSeconds"):
            if dist.parentNode == lap:
                time_val = float(dist.firstChild.data)
                break
        new_lap = Lap(dist_val, time_val)
        new_laps.append(new_lap)

    print new_laps
