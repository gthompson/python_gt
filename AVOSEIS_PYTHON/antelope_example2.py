#!/opt/antelope/python2.7.2-64/bin/python
import os, sys
sys.path.append(os.environ['ANTELOPE'] + "/data/python")
import antelope.datascope as datascope
import matplotlib as mpl
import numpy as np
if 'DISPLAY' in os.environ.keys():
        mpl.use("Agg")
import matplotlib.pyplot as plt

# command line arguments
if len(sys.argv) < 3:
        # stop program and print a usage message
        sys.exit("Not enough arguments")
dbpath = sys.argv[1]
if not(os.path.isfile(dbpath)):
	sys.exit("%s not found" % dbpath)
outfile = sys.argv[2]
subset_expr = ""
if len(sys.argv) > 3:
	subset_expr = sys.argv[3] # expression to use when subsetting database

# open the origin table, join to event table, subset for preferred origins
db = datascope.dbopen( dbpath, 'r')
db = db.lookup( table = 'origin' )
db = db.join('event')
db = db.subset("orid == prefor")
if subset_expr != "":
	db = db.subset(subset_expr)
db = db.sort('time')
n = db.nrecs()
origin_id = np.empty(n)
origin_ml = np.empty(n)
origin_epoch = np.empty(n)
for db[3] in range(n):
	(origin_id[db[3]], origin_ml[db[3]], origin_epoch[db[3]]) = db.getv('orid','ml','time')

# convert the origin times from Unix epoch format to datenum format (almost the same as MATLAB)
origin_time = mpl.dates.epoch2num(origin_epoch)

# close the database
db.free()
db.close()

# remove origins which have no Ml - marked with the null value -999.0 in Antelope/CSS3.0
# Note: we could have done this subsetting in Antelope (and that is generally better) but
# this way we get to see the np.where command
i = np.where( origin_ml != -999.0)
origin_time = origin_time[i]
origin_ml = origin_ml[i]

# How many origins left? Update n
n = np.alen(origin_ml)
if n>0:

	# create the figure canvas and add an axes object
	fig1 = plt.figure()
	ax = fig1.add_subplot(111)

        # plot the data - since we plot against dates, we use plot_date rather than plot
        ax.plot_date(origin_time, origin_ml, c='y', linestyle='o')
        ax.xaxis_date()

	# add a grid
        ax.grid(True)
	
	# rotate the x-axis labels (rotation=0 is horizontal, rotation=90 is vertical) 
        plt.setp( ax.get_xticklabels(), rotation=90, horizontalalignment='center', fontsize=7 )

	# add a ylabel
        ax.set_ylabel('Ml')

	# Let matplotlib automatically decide where to put date (x-axis) tick marks, and what style of labels to use
	x_locator = mpl.dates.AutoDateLocator()
	x_formatter = mpl.dates.AutoDateFormatter(x_locator)
        ax.xaxis.set_major_locator(x_locator)
        ax.xaxis.set_major_formatter(x_formatter)

	# save the figure to outfile at 130 dots per inch
	print "- saving to " + outfile
	fig1.savefig(outfile, dpi=130)



