import matplotlib.pyplot as pp
import matplotlib as mpl
import numpy as np
from scipy import stats as st
import datetime

import stats

COLORS = ['#08C43A', '#6B2747', 'b']
FONT_SIZE = 18

def MinuteFormatter(x, p):
    return "%02.d:%02.d" % (int(x / 60), x % 60)

def PlotAlt(workout):
    pp.figure()

    alt = workout.GetAltArray()
    dist = workout.GetDistArray()
    #print alt
    pp.plot(dist, alt)
    pp.show()

def PlotPace(workouts):
    pp.figure()
    ax = pp.subplot(111)

    for i,workout in enumerate(workouts):
        pace = workout.GetPace()
        lap_starts = workout.GetLapEnds()
        pp.plot(lap_starts, pace, "o--", markersize=12,
                    mfc=COLORS[i], label=workout.name,
                    color='k')

    pp.ylabel("Run pace (min / km)", fontsize=FONT_SIZE)
    pp.xlabel("Distance (km)", fontsize=FONT_SIZE)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(FONT_SIZE)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(FONT_SIZE)

    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(MinuteFormatter))

    pp.grid(color='b')
    pp.ylim([200, 450])
    pp.legend(loc='upper left', fancybox=True, fontsize=FONT_SIZE)

    pp.show()

def PlotPaceVsDistance(workouts):
    nitems = len(workouts)
    dist = np.zeros(nitems)
    pace = np.zeros(nitems)

    recent_dist = []
    recent_pace = []
    # Grab dist and pace data for all and lates runs
    for i, workout in enumerate(workouts):
        dist[i] = workout.GetTotalDist() / 1000.0 # in km
        pace[i] = workout.GetTotalTime() / dist[i]
      
        if datetime.datetime.now() - workout.GetStartTime() < datetime.timedelta(days=60):
            recent_dist.append(dist[i])
            recent_pace.append(pace[i])
        

    # Finally, do the scatters
    f = pp.figure()
    ax = pp.subplot(111)
    pp.scatter(dist, pace)
    pp.scatter(recent_dist, recent_pace, color='#08C43A')

    pp.ylabel("Run pace (min / km)")
    pp.xlabel("Run length (km)")

    pp.xlim([0, 47.0])
    pp.ylim([220, 370])

    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(MinuteFormatter))

    # Fit for all runs
    slope, intercept, r_value, p_value, std_err = st.linregress(dist, pace)
    regr_x = np.array([5, 42])
    regr_y = intercept + regr_x * slope 
    pp.plot(regr_x, regr_y, '--', color='k')
    pp.annotate("%.2f s/km^2" % slope, (regr_x[1] - 10.0, regr_y[1]))

    # Fit for recent runs
    slope, intercept, r_value, p_value, std_err = st.linregress(recent_dist, recent_pace)
    regr_x = np.array([5, 42])
    regr_y = intercept + regr_x * slope 
    pp.plot(regr_x, regr_y, '--', color='#08C43A')
    pp.annotate("%.2f s/km^2" % slope, (regr_x[1] - 10.0, regr_y[1]))

    pp.show()

def PlotDistanceAtPace(workouts):
    paces = []
    dists = []

    recent_dist = []
    recent_pace = []

    for workout in workouts:
        for lap in workout.laps:
            if lap.dist == 0.0:
                continue

            pace = lap.time / (lap.dist / 1000.0)
            paces.append(pace)
            dists.append(lap.dist / 1000.0)

            if datetime.datetime.now() - workout.GetStartTime() < datetime.timedelta(days=60):
                recent_dist.append(lap.dist / 1000.0)
                recent_pace.append(pace)

    pp.figure()
    ax = pp.subplot(111)

    pp.hist(paces, weights=dists, bins=30, range=[180, 480], color='#52730B')

    pp.hist(recent_pace, weights=recent_dist, bins=30, range=[180, 480], color='r')

    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(MinuteFormatter))

    pp.xlabel("Pace (min / km)")
    pp.ylabel("Total distance at pace (km)")

    pp.legend(["Total", "Last 60 days"])

    pp.show()

def PlotMonthlyDist(workouts):
    monthly = {}

    for workout in workouts:
        month = workout.GetStartTime().month
        year = workout.GetStartTime().year

        month = workout.GetStartTime().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not month in monthly:
            monthly[month] = 0.0
        monthly[month] += workout.GetTotalDist() / 1000.0


    pp.figure()
    ax = pp.subplot(111, aspect=0.4)

    n_items = len(monthly.keys())
    sort_ind = sorted(range(n_items), key=lambda i: monthly.keys()[i])
    months =  [monthly.keys()[ind] for ind in sort_ind]
    totals =  [monthly.values()[ind] for ind in sort_ind]

    AV_MONTHS = 3
    totals_av = []
    # get moving average
    for i in range(AV_MONTHS-1, n_items):
        total = 0.0
        for j in range(AV_MONTHS):
            total += totals[i-j]
        totals_av.append(total / AV_MONTHS)

    pp.plot(months, totals, 'o--', markersize=14, color='k', mfc='b')

    pp.plot(months[AV_MONTHS-1:], totals_av, 'o--', color='k', markersize=14, mfc='g')

    pp.legend(["Monthly", "3-month average"], loc='upper left')
    pp.ylim([0, 360])
    pp.xlim([months[0] - datetime.timedelta(days=31), months[-1] + datetime.timedelta(days=31)])

    ax.yaxis.grid(color='b')

    pp.ylabel("Total distance (km)")

    pp.show()
