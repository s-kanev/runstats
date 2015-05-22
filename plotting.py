import matplotlib.pyplot as pp
import matplotlib.dates
import matplotlib as mpl
import numpy as np
from scipy import stats as st
import datetime

import stats

COLORS = ['#08C43A', '#6B2747', 'b']
FONT_SIZE = 18

def MinuteFormatter(x, p):
    return "%02.d:%02.d" % (int(x / 60), x % 60)

def HourMinFormatter(x, p):
    return "%d:%02.d" % (int(x / 3600), int((x % 3600) / 60))

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
    #pp.ylim([200, 450])
    pp.legend(loc='lower left', fancybox=True, fontsize=FONT_SIZE)
    pp.tight_layout()

    pp.show()

def PlotPaceVsDistance(workouts, fname=None):
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
    pp.plot(dist, pace, "o", markersize=6)
    pp.plot(recent_dist, recent_pace, "o", mfc=COLORS[0], markersize=6)

    pp.ylabel("Run pace (min / km)", fontsize=FONT_SIZE)
    pp.xlabel("Run length (km)", fontsize=FONT_SIZE)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(FONT_SIZE)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(FONT_SIZE)


    pp.xlim([0, 47.0])
    pp.ylim([200, 370])

    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(MinuteFormatter))

    # Fit for all runs
    slope, intercept, r_value, p_value, std_err = st.linregress(dist, pace)
    regr_x = np.array([5, 42])
    regr_y = intercept + regr_x * slope 
    pp.plot(regr_x, regr_y, '--', color='k')
    pp.annotate("%.2f s/km^2" % slope, (regr_x[1] - 10.0, regr_y[1] - 10), fontsize=FONT_SIZE-2)

    # Fit for recent runs
    slope, intercept, r_value, p_value, std_err = st.linregress(recent_dist, recent_pace)
    regr_x = np.array([5, 42])
    regr_y = intercept + regr_x * slope 
    pp.plot(regr_x, regr_y, '--', color=COLORS[0])
    pp.annotate("%.2f s/km^2" % slope, (regr_x[1] - 10.0, regr_y[1] - 10), color=COLORS[0], fontsize=FONT_SIZE-2)

    ax.yaxis.grid(color='b')
    pp.legend(["Total", "Last 60 days"], loc='lower right', fancybox=True, fontsize=FONT_SIZE)

    pp.tight_layout()
    if fname:
        pp.savefig(fname)
    pp.show()

def PlotDistanceAtPace(workouts, fname=None):
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

    pp.xlabel("Pace (min / km)", fontsize=FONT_SIZE)
    pp.ylabel("Total distance at pace (km)", fontsize=FONT_SIZE)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(FONT_SIZE)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(FONT_SIZE)

    pp.legend(["Total", "Last 60 days"], loc='upper right', fancybox=True, fontsize=FONT_SIZE)
    pp.grid(color='b')

    pp.tight_layout()
    if fname:
        pp.savefig(fname)
    pp.show()

def PlotMonthlyDist(workouts, fname=None):
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

    pp.legend(["Monthly", "3-month average"], loc='upper left', fancybox=True, fontsize=FONT_SIZE)
    pp.xlim([months[0] - datetime.timedelta(days=14), months[-1] + datetime.timedelta(days=14)])

    ax.yaxis.grid(color='b')

    pp.ylabel("Total distance (km)", fontsize=FONT_SIZE)

    locator = mpl.dates.MonthLocator()
    formatter = mpl.dates.AutoDateFormatter(locator)
    formatter.scaled[30.0] = '%b' # only show month
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(FONT_SIZE)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(FONT_SIZE)

    pp.tight_layout()
    if fname:
        pp.savefig(fname)
    pp.show()

def PlotRaces(workouts, fname):
    pp.figure()
    ax = pp.subplot(111)

    race_times = []
    dates = []
    for workout in workouts:
        if workout.GetTotalDist() < 41.0 * 1000:
            continue

        race_times.append(workout.GetTotalTime())
        dates.append(workout.GetStartTime())


    pp.plot(dates, race_times, "o", markersize=12,
#                mfc=COLORS[i], label=workout.name,
                color='k')

    # calculate regression
    days_diff = np.arange(len(dates))
    for i,d in enumerate(dates):
        days_diff[i] = (d - min(dates)).days
    slope, intercept, r_value, p_value, std_err = st.linregress(days_diff, race_times)
    regr_y = intercept + days_diff * slope

    # plot regression
    pp.plot(dates, regr_y, "--", color='#555555', lw=1.5, label=None)
    month_slope = 30 * slope
    pp.text(0.35, 0.30,
            r"Trend: %d:%02.d / month" % (int(month_slope / 60),
                                          int(abs(month_slope) % 60)),
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes)

    pp.ylabel("Marathon time", fontsize=FONT_SIZE)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(FONT_SIZE)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(FONT_SIZE)
    pp.xticks(rotation=75)

    xmin = min(dates) - datetime.timedelta(weeks=4)
    xmax = max(dates) + datetime.timedelta(weeks=4)
    pp.xlim([xmin, xmax])
    ymin = 2 * 3600
    ymax = 4 * 3600 + 20 * 60
    pp.ylim([ymin, ymax])
    lim = (ax.get_xlim()[1] - ax.get_xlim()[0]) /\
          (ax.get_ylim()[1] - ax.get_ylim()[0])
    ax.set_aspect(0.3 * lim)

    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(HourMinFormatter))

    ax.set_axisbelow(True)
    pp.grid(ls="-", color="#cccccc")
    pp.tight_layout()
    if fname:
        pp.savefig(fname)
    pp.show()

def PlotYearlyCumulative(workouts, fname=None):
    workouts_ = sorted(workouts, key=lambda x: x.GetStartTime())

    years = []
    for w in workouts_:
        year = w.GetStartTime().year
        if year not in years:
            years.append(year)

    pp.figure()
    ax = pp.subplot(111)

    for year in years:
        year_start = datetime.date(year=year, month=1, day=1)
        cum_dist = 0.0
        days = []
        for i in range(366):
            days.append(year_start + datetime.timedelta(days=i))
        daily_cum_dist = np.zeros(366) * float("NaN")
        daily_cum_dist[0] = 0.0

        for w in workouts_:
            if w.GetStartTime().year != year:
                continue

            day_ind = (w.GetStartTime().date() - year_start).days

            cum_dist += w.GetTotalDist() / 1000.0
            daily_cum_dist[day_ind] = cum_dist

        # fixup days that didn't contribute
        for i,d in enumerate(days):
            if np.isnan(daily_cum_dist[i]) and d < datetime.date.today():
                daily_cum_dist[i] = daily_cum_dist[i-1]

        pp.plot(daily_cum_dist, label=str(year), lw=2)

    # sort both labels and handles by labels
    handles, labels = ax.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles), reverse=True))
    ax.legend(handles, labels,
              loc='upper left', fancybox=True, fontsize=FONT_SIZE)

    pp.xlim([0, 365])

    lim = (ax.get_xlim()[1] - ax.get_xlim()[0]) /\
          (ax.get_ylim()[1] - ax.get_ylim()[0])
    ax.set_aspect(0.3 * lim)

    ax.yaxis.grid(ls='-', color='#cccccc')

    pp.ylabel("Cumulative distance (km)", fontsize=FONT_SIZE)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(FONT_SIZE)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(FONT_SIZE)

    pp.tight_layout()
    if fname:
        pp.savefig(fname)
    pp.show()
