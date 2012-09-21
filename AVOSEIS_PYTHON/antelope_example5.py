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
import mymod
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
dictorigin, numevents = mymod.dbgetorigins(dbpath, subset_expr)

# if we loaded some events, create plots
if numevents > 0:

	###### PLOT DATA HERE 

	# Let matplotlib automatically decide where to put date (x-axis) tick marks, and what style of labels to use
	locator = mpl.dates.AutoDateLocator()
	formatter = mpl.dates.AutoDateFormatter(locator)

        # Compute reasonable binsize based on the first and last event times
        snum, enum, binsize = mymod.compute_binsize(dictorigin)

	# create the figure canvas
	fig1 = plt.figure()

	# add subplot - ml versus time
	ax1 = fig1.add_subplot(211)
	mymod.plot_time_ml(ax1, dictorigin, locator, formatter, snum, enum)

        # add subplot - counts versus time
        ax2 = fig1.add_subplot(212)
        mymod.plot_counts(ax2, dictorigin, locator, formatter, binsize, snum, enum)
	
	####### SAVE FIGURE

	# save the figure to outfile at 100 dots per inch
	print "- saving to " + outfile
	fig1.savefig(outfile, dpi=100)




