import matplotlib.pyplot as pp
import numpy as np

import stats


def PlotAlt(workout):
    pp.figure()

    alt = workout.GetAltArray()
    dist = workout.GetDistArray()
    #print alt
    pp.plot(dist, alt)
    pp.show()
