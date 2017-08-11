# -*- coding: utf-8 -*-

"""
Tracking predictive Gantt chart with matplotlib

"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import statsmodels as sm

def read_data(fname):
    """
    read the input file from the simulator snapshot at some timepoint

    form of the input file (in lines):
        timepoint
        current schedule (-1 for unstarted activities)
        current baseline schedule
        ideal new baseline schedule
        active activities
        unstarted activities
        start times samples (in separate line per each activity)
        end times samples (in separate line per each activity)

    """

    f = open(fname)

    timepoint = int(f.readline())

    text = f.readline()
    temp = text.split(' ')[:-1]
    sched = [int(i) for i in temp]

    text = f.readline()
    temp = text.split(' ')[:-1]
    baseline = [int(i) for i in temp]

    text = f.readline()
    temp = text.split(' ')[:-1]
    new_base = [int(i) for i in temp]

    text = f.readline()
    temp = text.split(' ')[:-1]
    realdurs = [int(i) for i in temp]

    text = f.readline()
    temp = text.split(' ')[:-1]
    actives = [int(i) for i in temp]

    text = f.readline()
    temp = text.split(' ')[:-1]
    unstarteds = [int(i) for i in temp]

    starts = []
    for i in xrange(len(sched)):
        text = f.readline()
        temp = text.split(' ')[:-1]
        if i not in unstarteds:
            starts.append([int(sched[i]),])
        else:
            starts.append([int(i) for i in temp])

    f.readline()
    ends = []
    for i in xrange(len(sched)):
        text = f.readline()
        temp = text.split(' ')[:-1]
        if i not in unstarteds and i not in actives:
            ends.append([int(realdurs[i]),])
        else:
            ends.append([int(i) for i in temp])

    f.close()
    return timepoint, starts, ends, baseline, new_base, realdurs, actives, unstarteds

def create_gantt_chart(num_act, starts, ends, baseline, new_baseline, timepoint=0,
                       max_time=0, figure_size=(10, 8), filename=None):
    """
        Create tracking gantt charts with matplotlib

        num_act - number of activities
        starts - simulation traces of start times
        ends - simulation traces of end times
        baseline - current baseline schedule
        new_baseline - ideal new baseline
        timepoint - point in time for this data
        max_time - maximum time on x axis if greater than any datapoint
        figure_size - size of the created figure
        filename - name of file to save

    """

    #num_act-1 is the last index, we ommit first dummy
    ylabels = range(1, num_act)

    ilen = len(ylabels)

    ylim_min = 0.2
    ylim_max = ilen*0.5+0.3
    xlim_min = 0

    #vertical positions for bars
    pos = np.arange(0.5, ilen*0.5+0.1, 0.5)

    #create plot and division between past and future
    fig = plt.figure(figsize=figure_size)
    ax = fig.add_subplot(111)
    if timepoint > 0:
        ax.add_patch(
            patches.Rectangle(
                (xlim_min, ylim_min),   # (x,y)
                timepoint-xlim_min,          # width
                ylim_max-ylim_min,          # height
                alpha=0.3,
                color="lightgrey"
                )
            )

    for i in range(len(ylabels)):
        xnew = np.arange(min(starts[i+1]), max(ends[i+1]), 1) #plot dimensions
        if len(xnew) == 0:
            continue
        max_time = max(max_time, xnew[-1])
        start_date = xnew[0]
        duration = xnew[-1]-start_date

        ax.barh((i*0.5)+0.5, duration, left=start_date,
                height=0.46, align='center', edgecolor='lightgrey',
                color='lightgrey', alpha=1)
        plt.text(start_date-0.8, pos[i], ylabels[i], fontsize=14)

        #add CDFs to the plot
        starts[i+1].sort()
        ends[i+1].sort()

        ecdf_starts = sm.distributions.ECDF(starts[i+1])
        ecdf_ends = sm.distributions.ECDF(ends[i+1])

        ax.plot(xnew, ((i+1)*0.5)-ecdf_ends(xnew)*0.46+0.23, color='#000000', linewidth=2)
        ax.plot(xnew, ((i+1)*0.5)-ecdf_starts(xnew)*0.46+0.23, color='#000000', linewidth=2)

        #add connecting segments to 0 if there isn't
        ax.plot([xnew[0], xnew[0]], [(i+1)*0.5+0.23, ((i+1)*0.5)-ecdf_starts(xnew[0])*0.46+0.23],
                color='#000000', linewidth=2)
        ax.plot([xnew[0], xnew[0]], [(i+1)*0.5+0.23, ((i+1)*0.5)-ecdf_ends(xnew[0])*0.46+0.23],
                color='#000000', linewidth=2)
        #add connecting for ending time in deterministic
        ax.plot([xnew[-1], xnew[-1]], [(i+1)*0.5-0.23, ((i+1)*0.5)-ecdf_ends(xnew[-1])*0.46+0.23],
                color='#000000', linewidth=2)#,linestyle='--')


        #plot baseline time
        ax.plot([baseline[i+1]-0.1, baseline[i+1]-0.1], [(i+1)*0.5+0.23, (i+1)*0.5-0.23],
                color='#000000', linewidth=3, linestyle='--')

        #plot ideal new baseline time
        if new_baseline[i+1] != baseline[i+1]:
            ax.plot([new_baseline[i+1]-0.1, new_baseline[i+1]-0.1], [(i+1)*0.5+0.23, (i+1)*0.5-0.23],
                    color='#000000', linewidth=3, linestyle=':')

    locsy, labelsy = plt.yticks(pos, ylabels)
    plt.setp(labelsy, fontsize=14)


    ax.axes.yaxis.set_ticklabels([])

    xlim_max = max_time+1

    ax.set_xlim(xmin=xlim_min, xmax=xlim_max)
    ax.set_ylim(ymin=ylim_min, ymax=ylim_max)
    ax.tick_params(axis=u'y', which=u'both', length=0)

    major_ticks = np.arange(0, max_time+1, 5)
    minor_ticks = np.arange(0, max_time+1, 1)

    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)

    # add x axis ticks to the plot
    ax.tick_params(axis=u'x', which=u'major', length=10, width=1)
    ax.tick_params(axis=u'x', which=u'minor', length=5, width=1)

    ax.set_axisbelow(True) #grid below other elements
    ax.grid(color='black', linestyle='solid', axis='x', linewidth=1, alpha=1)

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


    labelsx = ax.get_xticklabels()
    #labels on x axis
    plt.setp(labelsx, rotation=0, fontsize=14)

    #add arrow to bottom spine
    al = 7 # arrow length in points
    aw = 14 # arrow width in points
    arrowprops = dict(clip_on=False, # plotting outside axes on purpose
                      headlength=aw, # in points
                      headwidth=al, # in points
                      facecolor='k')
    kwargs = dict(
        xycoords='axes fraction',
        textcoords='offset points',
        arrowprops=arrowprops,
        )

    ax.annotate("", (1, 0), xytext=(-al, 0), **kwargs) # bottom spine arrow
    ax.invert_yaxis()

    if timepoint > 0:
        #add line for present
        ax.plot([timepoint, timepoint], [ylim_min, ylim_max],
                color='#000000', linewidth=1, linestyle='--')

    if filename is not None:
        plt.savefig(filename)
    plt.show()

if __name__ == '__main__':
    fname = r"./data/ProjSnap7_4.txt"
    timepoint, starts, ends, baseline, new_base, _, _, _ = read_data(fname)
    create_gantt_chart(len(baseline), starts, ends, baseline, new_base,
                       timepoint, filename="gantt_4.svg")
    