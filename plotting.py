import matplotlib.pyplot as pp
import matplotlib as mpl
import numpy as np
from scipy import stats as st

import stats


def PlotAlt(workout):
    pp.figure()

    alt = workout.GetAltArray()
    dist = workout.GetDistArray()
    #print alt
    pp.plot(dist, alt)
    pp.show()

def minuteFormatter(x, p):
    return "%02.d:%02.d" % (int(x / 60), x % 60)

def PlotPaceVsDistance(workouts):
    nitems = len(workouts)
    dist = np.zeros(nitems)
    pace = np.zeros(nitems)

    for i, workout in enumerate(workouts):
        dist[i] = workout.GetTotalDist() / 1000.0 # in km
        pace[i] = workout.GetTotalTime() / dist[i]
        

    f = pp.figure()
    ax = pp.subplot(111)
    pp.scatter(dist, pace)

    pp.ylabel("Run pace (min / km)")
    pp.xlabel("Run length (km)")

    pp.xlim([0, 47.0])
    pp.ylim([270, 370])

    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(minuteFormatter))

    slope, intercept, r_value, p_value, std_err = st.linregress(dist, pace)
    regr_x = np.array([5, 42])
    regr_y = intercept + regr_x * slope 
    pp.plot(regr_x, regr_y, '--', color='k')
    pp.annotate("%.0f s/km^2" % slope, (regr_x[1] - 10.0, regr_y[1]))

    pp.show()
