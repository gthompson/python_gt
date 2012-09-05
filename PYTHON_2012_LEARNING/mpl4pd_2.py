#!/opt/antelope/python2.7.2-64/bin/python
###############################
#a GT ANTELOPE OBSPY HEADER
import sys, os
sys.path.append(os.environ['ANTELOPE'] + "/data/python")

# OBSPY_EXT by Mark Williams
#sys.path.append("/Users/glenn/src/obspy_ext/antelope")
#import core

# Stuff in an Antelope-python example
#import signal
#signal.signal(signal.SIGINT, signal.SIG_DFL)

# Antelope stuff
import antelope.datascope as datascope

# numpy & matplotlib
import matplotlib as mpl
import numpy as np
from datetime import datetime
#import matplotlib.mlab as mlab
if 'DISPLAY' in os.environ.keys():
	mpl.use("Agg")
import matplotlib.pyplot as plt
#import pylab

# note that global/default mpl settings can be given in config files at the global, user home and pwd levels - see p44

# END OF GT ANTELOPE-OBSPY HEADER
#################################
dbpath = '/Seis/Kiska4/picks/Total/Total'
subset_expr = "ml > 2.5 && time > \"2000/01/01\""
#dbcreate('mydb', 'css3.0', '/opt/antelope/data/db/demo/demo', 'a temporary database created by Glenn', 'Some details about the database')
#db = datascope.dbopen( '/opt/antelope/data/db/demo/demo', 'r')
db = datascope.dbopen( dbpath, 'r')
db = db.lookup( table = 'origin' )
db = db.subset(subset_expr)
n = db.nrecs()
print "Number of records: {}".format(n)
# if size of arrays already known, preallocation much faster than recreating each time with append
origin_id = np.empty(n)
origin_ml = np.empty(n)
origin_epoch = np.empty(n)
origin_datetime = np.empty(n)
for db[3] in range(n):
	(origin_id[db[3]],origin_ml[db[3]],origin_epoch[db[3]]) = db.getv('orid','ml','time')
	#origin_datetime[db[3]] = datetime.fromtimestamp(origin_epoch[db[3]])
	origin_datetime[db[3]] = mpl.dates.epoch2num(origin_epoch[db[3]])
db.free()
db.close()
#print origin_epoch

fig1 = plt.figure()
ax1 = fig1.add_subplot(111)
ax1.plot_date(origin_datetime, origin_ml, linestyle='.')
# What are the axis limits?
ax1.axis()
# Set the axis limits, can also set with plt.xlim([xmin, xmax]) or plt.axis(xmin=XMIN, ...) to change one or many limits at a tme
#ax1.axis([0, 5, -1, 13])
# Add a grid
ax1.grid(True)
# Add titles and labels
ax1.set_title("db: " + dbpath + "\n" + "subset: " + subset_expr)
ax1.set_xlabel('Year')
ax1.set_ylabel('Ml')
#ax1.legend(loc='upper left')
yearsLoc = mpl.dates.YearLocator()
yearsFmt = mpl.dates.DateFormatter('%Y')
ax1.xaxis.set_major_formatter(yearsFmt)
fig1.autofmt_xdate()
# What is the figure size in inches?
mpl.rcParams['figure.figsize']
# How many dots per inch?
mpl.rcParams['savefig.dpi']
# Save it
fig1.savefig('plots/plot2.png', dpi=130)
#fig1.show()
# the following does not work on RHEL
#os.system("open myplot.png")

