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
# main program
#################################
######## USAGE
usage = """%s /path/to/database outputfile [subset_expr]

	where subset_expr is an optional dbeval (Datascope) subset expression 

	your database must have an origin and event table present
	
	e.g. plot all earthquakes from the AVO catalog with Ml>=1.0 within 20km of Iliamna since 1994/01/01
	
	%s /Seis/Kiska4/picks/Total/Total iliamna_energy.png 'ml >= 1.0 && time > \"1994/01/01\" && deg2km(distance(lat, lon, 60.0319, -153.0918))<20.0'
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

######## OPEN A POINTER TO THE VIEW OF PREFERRED ORIGINS FROM THE DATABASE
# open the origin table, join to event table, subset for preferred origins
db = datascope.dbopen( dbpath, 'r')
db = db.lookup( table = 'origin' )
db = db.join('event')
db = db.subset("orid == prefor")

# SO FAR THE HEADER AND MAIN PROGRAM ARE THE SAME AS FOR dbploteventcounts. But
# to save work, here we simply import functions we need from that script.
import giseistools2 as giseistools

######## LOAD THE EVENTS 
# load events from the database dbpath, and apply subset_expr if there is one
dictorigin = dict();
dictorigin, numevents = giseistools.dbgetorigins(db, subset_expr)

# if we loaded some events, create plots
if numevents > 0:

	###### PLOT DATA HERE 

	# Compute bin_edges based on the first and last event times
	bin_edges, snum, enum = giseistools.compute_binsize(dictorigin)

	# Let matplotlib automatically decide where to put date (x-axis) tick marks, and what style of labels to use
	locator = mpl.dates.AutoDateLocator()
	formatter = mpl.dates.AutoDateFormatter(locator)

	# create the figure canvas
	fig1 = plt.figure()

	# add subplot - ml versus time
	ax1 = fig1.add_subplot(311)
	giseistools.plot_time_ml(ax1, dictorigin, locator, formatter, snum, enum)
	
	# add subplot - counts versus time
	ax2 = fig1.add_subplot(312)
	giseistools.plot_counts(ax2, dictorigin, locator, formatter, bin_edges, snum, enum)
	
	# add subplot - energy versus time
	ax3 = fig1.add_subplot(313)
	giseistools.plot_energy(ax3, dictorigin, locator, formatter, bin_edges, snum, enum)

	####### SAVE FIGURE

	# save the figure to outfile at 130 dots per inch
	print "- saving to " + outfile
	fig1.savefig(outfile, dpi=130)

##### CLOSE DATABASE
db.free()
db.close()

