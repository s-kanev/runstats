#!/bin/python

import argparse
from xml.dom.minidom import parse
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

########################################################################
def ParseLap(lap_element):

    # Get lap totals -- time and distance
    for dist in lap_element.getElementsByTagName("DistanceMeters"):
        if dist.parentNode == lap_element:
            dist_val = float(dist.firstChild.data)
            break
    for time in lap_element.getElementsByTagName("TotalTimeSeconds"):
        if time.parentNode == lap_element:
            time_val = float(time.firstChild.data)
            break

    new_lap = Lap()
    new_lap.SetTotals(dist_val, time_val)

    start_time = lap_element.getAttribute("StartTime")
    new_lap.SetStart(datetime.strptime(start_time, TIME_FORMAT))

    # Get GPS trackpoints
    for track in lap_element.getElementsByTagName("Track"):
        if track.parentNode == lap_element:
            break

    for trackpoint in track.getElementsByTagName("Trackpoint"):
        if trackpoint.parentNode == track:
            new_tp = TrackPoint()

            for alt in trackpoint.getElementsByTagName("AltitudeMeters"):
                if alt.parentNode == trackpoint:
                    new_tp.alt = float(alt.firstChild.data)
                    break

            for dist in trackpoint.getElementsByTagName("DistanceMeters"):
                if dist.parentNode == trackpoint:
                    new_tp.cum_dist = float(dist.firstChild.data)
                    break

            # XXX: proper corner cases
            if new_tp.alt != -1 and new_tp.cum_dist != -1:
                new_lap.AddPoint(new_tp)

    return new_lap

########################################################################
def ParseDoc(doc_name):
    try:
        doc = parse(doc_name)
    except:
        return None

    workout = Workout()

    new_laps = []
    laps = doc.getElementsByTagName("Lap")
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
        workout = ParseDoc(fname)
        plotting.PlotAlt(workout)

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
