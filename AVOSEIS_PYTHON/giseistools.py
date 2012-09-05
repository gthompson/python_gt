#!/opt/antelope/python2.7.2-64/bin/python
##### THIS IS A GOOD HEADER TO USE FOR ANTELOPE-MATPLOTLIB TOOLS
import os, sys
sys.path.append(os.environ['ANTELOPE'] + "/data/python")
import antelope.datascope as datascope
import matplotlib as mpl
import numpy as np
if 'DISPLAY' in os.environ.keys():
	mpl.use("Agg")
import matplotlib.pyplot as plt
import datetime
#################################
def dbgetorigins(dborigin, subset_expr):
	# load origins from database
	dbptr = dborigin.subset(subset_expr)
	dbptr = dbptr.sort('time')
	n = dbptr.nrecs()
	print "- number of events = {}".format(n)

	# if size of arrays already known, preallocation much faster than recreating each time with append
	dictorigin = dict()
	origin_id = np.empty(n)
	origin_ml = np.empty(n)
	origin_epoch = np.empty(n)
	for dbptr[3] in range(n):
		(origin_id[dbptr[3]], origin_ml[dbptr[3]], origin_epoch[dbptr[3]]) = dbptr.getv('orid','ml','time')
	dictorigin['id'] = origin_id
	dictorigin['ml'] = origin_ml
	dictorigin['time'] = mpl.dates.epoch2num(origin_epoch)
	return dictorigin, n

def plot_time_ml(ax, dictorigin, x_locator, x_formatter, snum, enum):
	time = dictorigin['time']
	ml = dictorigin['ml']
	# we do not want to plot Ml = -999.0, the Antelope value for a non-existent Ml - filter them out
	i = np.where( ml > -3.0)
	time = time[i]
	ml = ml[i]

	# plot the data
	ax.plot_date(time, ml, linestyle='yo')
	ax.grid(True)
	ax.xaxis_date()
	plt.setp( ax.get_xticklabels(), rotation=90, horizontalalignment='center', fontsize=7 )
	ax.set_ylabel('Ml')
	ax.xaxis.set_major_locator(x_locator)
	ax.xaxis.set_major_formatter(x_formatter)
	ax.set_xlim(snum, enum)
	return

def plot_counts(ax, dictorigin, x_locator, x_formatter, binsize, snum, enum):
	# bin the data
	bins = np.arange(snum, enum, binsize)
	events, edges, patches = ax.hist(dictorigin['time'], bins, cumulative=False, histtype='bar', color='0.75')
	ax.grid(True)
	ax.xaxis_date()
	plt.setp( ax.get_xticklabels(), rotation=90, horizontalalignment='center', fontsize=7 )
	ax.set_ylabel("Counts")
	ax.xaxis.set_major_locator(x_locator)
	ax.xaxis.set_major_formatter(x_formatter)
	ax.set_xlim(snum, enum)
		
	time = dictorigin['time']
	cumcounts = np.arange(1,np.alen(time)+1)
	ax2 = ax.twinx()
	p2, = ax2.plot(time,cumcounts,'g')
	ax2.yaxis.get_label().set_color(p2.get_color())
	ax2.set_ylabel("Cumulative")
	ax2.xaxis.set_major_locator(x_locator)
	ax2.xaxis.set_major_formatter(x_formatter)
	ax2.set_xlim(snum, enum)
	return

def floor(myvector, binsize):
	# rather than floor to the next lowest integer (i.e. multiple of 1), floor to the next lowest multiple of binsize
	return np.floor(myvector / binsize) * binsize  

def ceil(myvector, binsize):
	# rather than ceil to the next highest integer (i.e. multiple of 1), ceil to the next highest multiple of binsize
	return np.ceil(myvector / binsize) * binsize  

def compute_binsize(dictorigin):
        # based on the times of the events loaded, lets compute a reasonable number for the start and end time to use for each subplot,
        # and also a reasonable binsize
        # First lets calculate the difference in time between the first and last events
        time_firstevent = np.min(dictorigin['time'])
        time_lastevent = np.max(dictorigin['time'])
        daysdiff = time_lastevent - time_firstevent
        # Try and keep to around 100 bins or less
        if daysdiff <= 2/24:  # less than 2 hours of data, use a binsize of 1 minute
                binsize = 1/1440
		# Now roundoff the start and end times based on the binsize
        	snum = floor(time_firstevent, binsize) # start time
        	enum = ceil(time_lastevent, binsize) # end time
		bins = np.arange(snum, enum, binsize)
        elif daysdiff <= 4:  # less than 4 days of data, use a binsize of 1 hour
                binsize = 1/24
		# Now roundoff the start and end times based on the binsize
        	snum = floor(time_firstevent, binsize) # start time
        	enum = ceil(time_lastevent, binsize) # end time
		bins = np.arange(snum, enum, binsize)
        elif daysdiff <= 100:  # less than 100 days of data, use a binsize of 1 day
                binsize = 1
		# Now roundoff the start and end times based on the binsize
        	snum = floor(time_firstevent, binsize) # start time
        	enum = ceil(time_lastevent, binsize) # end time
		bins = np.arange(snum, enum, binsize)
        elif daysdiff <= 700: # less than 700 days of data, use a binsize of 1 week
                binsize = 7
		# Now roundoff the start and end times based on the binsize
        	snum = floor(time_firstevent, binsize) # start time
        	enum = ceil(time_lastevent, binsize) # end time
		bins = np.arange(snum, enum, binsize)
        elif daysdiff <= 3000: # less than 3000 days of data, use a binsize of (approx) 1 month
                binsize = 365.26/12
        	snum = floor(time_firstevent, binsize) # start time
		# because a month isn't exactly 365.26/12 days, this is not going to be the month boundary
		# so let us get the year and the month for snum, but throw away the day, hour, minute, second etc
		sdate = mpl.dates.num2date(snum)
		sdate = datetime.datetime(sdate.year, sdate.month, 1, 0, 0, 0)
		thisyear = sdate.year
		thismonth = sdate.month
		snum = mpl.dates.date2num(sdate)
		bins = list()
		bins.append(snum) 
		count = 0
		while bins[count] < time_lastevent:
			count += 1
			thismonth += 1
			if thismonth > 12: # datetime.datetime dies if sdate.month > 12
				thisyear += 1
				thismonth -= 12
			monthdate = datetime.datetime(thisyear, thismonth, 1, 0, 0, 0)
			bins.append(mpl.dates.date2num(monthdate))
		bins = np.array(bins)
		enum = np.max(bins)
        else:
                binsize = 365.26 # otherwise use a binsize of 1 year
        	snum = floor(time_firstevent, binsize) # start time
		# because a year isn't exactly 365.26 days, this is not going to be the year boundary
		# so let us get the year for snum, but throw away the month, day, hour, minute, second etc
		sdate = mpl.dates.num2date(snum)
		sdate = datetime.datetime(sdate.year, 1, 1, 0, 0, 0)
		snum = mpl.dates.date2num(sdate)
		bins = list()
		bins.append(snum) 
		count = 0
		while bins[count] < time_lastevent:
			count += 1
			yeardate = datetime.datetime(sdate.year + count, 1, 1, 0, 0, 0)
			bins.append(mpl.dates.date2num(yeardate))
		bins = np.array(bins)
		enum = np.max(bins)

	return bins, snum, enum, binsize


