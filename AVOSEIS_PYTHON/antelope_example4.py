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

#################################
# SUBROUTINES 
#################################

def dbgetorigins(dbpath, subset_expr):
	# open the origin table, join to event table, subset for preferred origins
	db = datascope.dbopen( dbpath, 'r')
	dborigin = db.lookup( table = 'origin' )
	dborigin = dborigin.join('event')
	dborigin = dborigin.subset("orid == prefor")

	# apply the optional subset expression if there is one, order by time, and display number of events.
	dborigin = dborigin.subset(subset_expr)
	dborigin = dborigin.sort('time')
	n = dborigin.nrecs()
	print "- number of events = {}".format(n)

	# if size of arrays already known, preallocation much faster than recreating each time with append
	dictorigin = dict()
	origin_id = np.empty(n)
	origin_ml = np.empty(n)
	origin_epoch = np.empty(n)

	# load origins from database and store them in a dictionary
	for dborigin[3] in range(n):
		(origin_id[dborigin[3]], origin_ml[dborigin[3]], origin_epoch[dborigin[3]]) = dborigin.getv('orid','ml','time')
	dictorigin['id'] = origin_id
	dictorigin['ml'] = origin_ml
	dictorigin['time'] = mpl.dates.epoch2num(origin_epoch)

	# close the database and free the memory. 
	# It seems that db.close and db.free both close the database, and closing twice produces error
	db.free()

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
        elif daysdiff <= 4:  # less than 4 days of data, use a binsize of 1 hour
                binsize = 1/24
        elif daysdiff <= 100:  # less than 100 days of data, use a binsize of 1 day
                binsize = 1
        elif daysdiff <= 700: # less than 700 days of data, use a binsize of 1 week
                binsize = 7
        elif daysdiff <= 3000: # less than 3000 days of data, use a binsize of (approx) 1 month
                binsize = 365.26/12
        else:
                binsize = 365.26 # otherwise use a binsize of 1 year

        # Now roundoff the start and end times based on the binsize
        snum = floor(time_firstevent, binsize) # start time
        enum = ceil(time_lastevent, binsize) # end time

        return snum, enum, binsize


#################################
# main program
#################################
######## USAGE
usage = """%s /path/to/database outputfile [subset_expr]

	where subset_expr is an optional dbeval (Datascope) subset expression 

	your database must have an origin and event table present
	
	e.g. plot all earthquakes from the AVO catalog with Ml>=1.0 within 20km of Iliamna since 1994/01/01
	
	%s /Seis/Kiska4/picks/Total/Total iliamna_counts.png 'ml >= 1.0 && time > \"1994/01/01\" && deg2km(distance(lat, lon, 60.0319, -153.0918))<20.0'
	""" % (sys.argv[0], sys.argv[0])

######## COMMAND LINE ARGUMENTS
if len(sys.argv) < 3:
        # stop program and print a usage message
        sys.exit(usage)
dbpath = sys.argv[1]
if not(os.path.isfile(dbpath)):
	sys.exit("%s not found" % dbpath)
outfile = sys.argv[2]
subset_expr = ""
if len(sys.argv) > 3:
	subset_expr = sys.argv[3] # expression to use when subsetting database
print "dbpath = " + dbpath
print "outfile = " + outfile
print "subset_expr = " + subset_expr

######## LOAD THE EVENTS 
# load events from the database dbpath, and apply subset_expr if there is one
dictorigin = dict();
dictorigin, numevents = dbgetorigins(dbpath, subset_expr)

# if we loaded some events, create plots
if numevents > 0:

	###### PLOT DATA HERE 

	# Let matplotlib automatically decide where to put date (x-axis) tick marks, and what style of labels to use
	locator = mpl.dates.AutoDateLocator()
	formatter = mpl.dates.AutoDateFormatter(locator)

        # Compute reasonable binsize based on the first and last event times
        snum, enum, binsize = compute_binsize(dictorigin)

	# create the figure canvas
	fig1 = plt.figure()

	# add subplot - ml versus time
	ax1 = fig1.add_subplot(211)
	plot_time_ml(ax1, dictorigin, locator, formatter, snum, enum)

        # add subplot - counts versus time
        ax2 = fig1.add_subplot(212)
        plot_counts(ax2, dictorigin, locator, formatter, binsize, snum, enum)
	
	####### SAVE FIGURE

	# save the figure to outfile at 100 dots per inch
	print "- saving to " + outfile
	fig1.savefig(outfile, dpi=100)




