#!/bin/python

import argparse
from lxml import etree
from datetime import datetime
import numpy as np
import os

import plotting

TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

########################################################################
class TrackPoint:
    def __init__(self):
        self.time = datetime.min
        self.lat = -1
        self.lon = -1
        self.alt = -1
        self.cum_dist = -1

########################################################################
class Lap:
    def __init__(self): 
        self.dist = -1
        self.time = -1
        self.start_time = datetime.min
        self.points = []

    def SetTotals(self, dist, time):
        self.dist = dist
        self.time = time

    def SetStart(self, start):
        self.start_time = start

    def AddPoint(self, tp):
        self.points.append(tp)

    def __str__(self):
        return ("%f %f" % (self.dist, self.time))
    def __repr__(self):
        return ("%f %f" % (self.dist, self.time))

########################################################################
class Workout:
    def __init__(self):
        self.laps = []
        self.name = "<None>"

    def AddLap(self, lap_element):
        self.laps.append(ParseLap(lap_element))

    def GetNumPoints(self):
        total = 0
        for lap in self.laps:
            total += len(lap.points)
        return total

    def GetAltArray(self):
        n_items = self.GetNumPoints()
        alt = np.zeros(n_items)
        i = 0
        for lap in self.laps:
            for tp in lap.points:
                alt[i] = tp.alt
                i += 1
        return alt

    def GetDistArray(self):
        n_items = self.GetNumPoints()
        dist = np.zeros(n_items)
        i = 0
        for lap in self.laps:
            for tp in lap.points:
                dist[i] = tp.cum_dist
                i += 1
        return dist

    def GetTotalDist(self):
        dist = 0.0
        for lap in self.laps:
            dist += lap.dist
        return dist

    def GetTotalTime(self):
        time = 0.0
        for lap in self.laps:
            time += lap.time
        return time

    def GetStartTime(self):
        return self.laps[0].start_time

    def GetPace(self):
        res = []
        for lap in self.laps:
            if lap.dist == 0.0:
                continue

            pace = lap.time / (lap.dist / 1000.0) # s / km
            res.append(pace)
        return res

    def GetLapStarts(self):
        res = []
        start = 0.0
        for lap in self.laps:
            if lap.dist == 0.0:
                continue

            res.append(start)
            start += lap.dist / 1000.0
        return res

    def GetLapEnds(self):
        res = []
        end = 0.0
        for lap in self.laps:
            if lap.dist == 0.0:
                continue

            end += lap.dist / 1000.0
            res.append(end)
        return res
########################################################################
def ParseLap(lap_element):

    # Get lap totals -- time and distance
    dist = lap_element.find('./{*}DistanceMeters')
    dist_val = float(dist.text)

    time = lap_element.find('./{*}TotalTimeSeconds')
    time_val = float(time.text)

    new_lap = Lap()
    new_lap.SetTotals(dist_val, time_val)

    start_time = lap_element.get("StartTime")
    new_lap.SetStart(datetime.strptime(start_time, TIME_FORMAT))

    track = lap_element.find("./{*}Track")
    if track is None:
        # No trackpoints, just return
        return new_lap

    # Get GPS trackpoints
    for trackpoint in track.findall("./{*}Trackpoint"):
        new_tp = TrackPoint()

        try:
            new_tp.alt = float(trackpoint.find("./{*}AltitudeMeters").text)
            new_tp.cum_dist = float(trackpoint.find("./{*}DistanceMeters").text)
        except AttributeError:
            # Some trackpoints only have a timestamp
            continue

        # XXX: proper corner cases
        if new_tp.alt != -1 and new_tp.cum_dist != -1:
            new_lap.AddPoint(new_tp)

    return new_lap

########################################################################
def ParseDoc(doc_name):
    try:
        docroot = etree.parse(doc_name).getroot()
    except:
        return None

    workout = Workout()

    name = docroot.find('./{*}Activities/{*}Activity/{*}Name')
    if name is not None:
        workout.name = name.text

    laps = docroot.findall('./{*}Activities/{*}Activity/{*}Lap')
    for lap_element in laps:
        workout.AddLap(lap_element)

    return workout

########################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fname")
    parser.add_argument("--path")
    args = parser.parse_args()
    fname = args.fname
    path = args.path

    if fname != None:
        fnames = fname.split(",")
        print fnames
 
        workouts = []
        for f in fnames:
            workouts.append(ParseDoc(f))
        plotting.PlotPace(workouts)
#        plotting.PlotAlt(workout)

    if path != None:
        workouts = []
        for f in os.listdir(path):
            if os.path.splitext(f)[1] != ".tcx":
                continue

            workout = ParseDoc(os.path.join(path, f))
            if workout == None:
                print "Ignoring workout %s" % f
                continue
            workouts.append(workout)

        plotting.PlotPaceVsDistance(workouts)
        plotting.PlotDistanceAtPace(workouts)
        plotting.PlotMonthlyDist(workouts)
