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
def plot_energy(ax, dictorigin, x_locator, x_formatter, bins, binsize, snum, enum):
	time = dictorigin['time']
        ml = dictorigin['ml']
        energy = np.power(10, 1.5 * ml)

	# bin the data as for counts
	#events, edges, patches = ax.hist(time, bins, cumulative=False, histtype='bar', color='0.75')
	events, edges = np.histogram(time, bins)
	#print events
	i_start = 0
	i_end = -1
	binned_energy = np.empty(np.alen(events))
	
	for binnum in range(np.alen(events)):
		i_end += events[binnum]
		if i_start <= i_end:
			#mystr = "%d: %d to %d: " % (binnum, i_start, i_end)
			#for i in np.arange(i_start, i_end+1):
				#mystr += " + %f" % energy[i]
			binned_energy[binnum] = np.sum(energy[i_start:i_end+1])
			#mystr += " = %f" % binned_energy[binnum]
			#print mystr
		else:
			#print "%d: no events" % (binnum)
			binned_energy[binnum] = 0
		i_start = i_end + 1
	#print mpl.dates.num2date(edges)
	#print mpl.dates.num2date(bins)
	#centers = np.delete(edges + binsize/2, np.alen(edges)-1)
	#print centers
	#ax.bar(centers, binned_energy)
	print np.alen(bins[:-1])
	print np.alen(binned_energy)
	barwidth = bins[1:] - bins[0:-1]
	ax.bar(bins[:-1], binned_energy, width=barwidth)

	# relable the y-axis in terms of equivalent Ml rather than energy
        yticklocs1 = ax.get_yticks()
        ytickvalues1 = np.log10(yticklocs1) / 1.5
        yticklabels1 = list()
        for count in range(len(ytickvalues1)):
                yticklabels1.append("%.2f" % ytickvalues1[count])
        ax.set_yticks(yticklocs1)
        ax.set_yticklabels(yticklabels1)
		
	ax.grid(True)
	ax.xaxis_date()
	plt.setp( ax.get_xticklabels(), rotation=90, horizontalalignment='center', fontsize=7 )
	ax.set_ylabel("Ml per bin")
	ax.xaxis.set_major_locator(x_locator)
	ax.xaxis.set_major_formatter(x_formatter)
	ax.set_xlim(snum, enum)
	#ax.yaxis.get_label().set_color(p1.get_color())
		

        cumenergy = np.cumsum(energy)
	ax2 = ax.twinx()
	p2, = ax2.plot(time,cumenergy,'g')

	# use the same ytick locations as for the left-hand axis, but label them in terms of equivalent cumulative magnitude
        yticklocs1 = ax.get_yticks()
        yticklocs2 = (yticklocs1 / max(ax.get_ylim())) * max(ax2.get_ylim() )
        ytickvalues2 = np.log10(yticklocs2) / 1.5
        yticklabels2 = list()
        for count in range(len(ytickvalues2)):
                yticklabels2.append("%.2f" % ytickvalues2[count])
        ax2.set_yticks(yticklocs2)
        ax2.set_yticklabels(yticklabels2)

	ax2.yaxis.get_label().set_color(p2.get_color())
	ax2.set_ylabel("Cumulative")
	ax2.xaxis.set_major_locator(x_locator)
	ax2.xaxis.set_major_formatter(x_formatter)
	ax2.set_xlim(snum, enum)
	return


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
print "dbpath = " + dbpath
print "outfile = " + outfile
print "subset_expr = " + subset_expr

######## OPEN A POINTER TO THE VIEW OF PREFERRED ORIGINS FROM THE DATABASE
# open the origin table, join to event table, subset for preferred origins
db = datascope.dbopen( dbpath, 'r')
db = db.lookup( table = 'origin' )
db = db.join('event')
db = db.subset("orid == prefor")

# SO FAR THE HEADER AND MAIN PROGRAM ARE THE SAME AS FOR dbploteventcounts. But
# to save work, here we simply import functions we need from that script.
# This is leading to some annyoing warnings. Lets suppress them
import warnings
warnings.filterwarnings("ignore")
import giseistools

######## LOAD THE EVENTS 
# load events from the database dbpath, and apply subset_expr if there is one
dictorigin = dict();
dictorigin, numevents = giseistools.dbgetorigins(db, subset_expr)

# if we loaded some events, create plots
if numevents > 0:

	###### PLOT DATA HERE 

	# Compute reasonable binsize based on the first and last event times
	bins, snum, enum, binsize = giseistools.compute_binsize(dictorigin)

	# Let matplotlib automatically decide where to put date (x-axis) tick marks, and what style of labels to use
	locator = mpl.dates.AutoDateLocator()
	formatter = mpl.dates.AutoDateFormatter(locator)

	# create the figure canvas
	fig1 = plt.figure()

	# add subplot - ml versus time
	ax1 = fig1.add_subplot(211)
	giseistools.plot_time_ml(ax1, dictorigin, locator, formatter, snum, enum)
	
	# add subplot - counts versus time
	ax2 = fig1.add_subplot(212)
	plot_energy(ax2, dictorigin, locator, formatter, bins, binsize, snum, enum)

	####### SAVE FIGURE

	# save the figure to outfile at 130 dots per inch
	print "- saving to " + outfile
	fig1.savefig(outfile, dpi=130)

##### CLOSE DATABASE
db.free()
db.close()

