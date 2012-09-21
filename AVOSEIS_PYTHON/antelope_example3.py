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

def plot_time_ml(ax, dictorigin, x_locator, x_formatter):
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
	return

#################################
# main program
#################################
######## USAGE
usage = """%s /path/to/database outputfile [subset_expr]

	where subset_expr is an optional dbeval (Datascope) subset expression 

	your database must have an origin and event table present
	
	e.g. plot all earthquakes from the AVO catalog with Ml>=1.0 within 20km of Iliamna since 1994/01/01
	
	%s /Seis/Kiska4/picks/Total/Total iliamna_ml_vs_time.png 'ml >= 1.0 && time > \"1994/01/01\" && deg2km(distance(lat, lon, 60.0319, -153.0918))<20.0'
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

	# create the figure canvas
	fig1 = plt.figure()

	# add subplot - ml versus time
	ax1 = fig1.add_subplot(111)
	plot_time_ml(ax1, dictorigin, locator, formatter)
	
	####### SAVE FIGURE

	# save the figure to outfile at 130 dots per inch
	print "- saving to " + outfile
	fig1.savefig(outfile, dpi=130)




