#!/opt/antelope/python2.7.2-64/bin/python
###############################
# GT ANTELOPE OBSPY HEADER
###############################
import sys, os
sys.path.append(os.environ['ANTELOPE'] + "/data/python")

# Antelope stuff
import antelope.datascope as datascope

# numpy & matplotlib
import matplotlib as mpl
import numpy as np
if 'DISPLAY' in os.environ.keys():
	mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.dates import epoch2num 

# note that global/default mpl settings can be given in config files at the global, user home and pwd levels - see p44

# END OF GT ANTELOPE-OBSPY HEADER
#################################
# subroutines
#################################

def dbgetorigins(dborigin, subset_expr):
	# load origins from database
	dbptr = dborigin.subset(subset_expr)
	n = dbptr.nrecs()
	print "Events in last year: {}".format(n)

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
	return dictorigin

def plot_time_ml(ax, dictorigin, x_locator, x_formatter, snum, enum):
	# plot the data
	ax.plot_date(dictorigin['time'], dictorigin['ml'], linestyle='.')
	ax.grid(True)
	ax.xaxis_date()
	plt.setp( ax.get_xticklabels(), rotation=90, horizontalalignment='center', fontsize=8 )
	ax.set_ylabel('Ml')
	ax.xaxis.set_major_locator(x_locator)
	ax.xaxis.set_major_formatter(x_formatter)
	ax.set_xlim(snum, enum)
	return

def plot_binnedtime_counts(ax, dictorigin, x_locator, x_formatter, binsize, ylabel, snum, enum):
	# bin the data
	#snum = np.floor(dictorigin['time'].min())
	#enum = np.ceil(dictorigin['time'].max())
	bins = np.arange(snum, enum, binsize)
	y = ax.hist(dictorigin['time'], bins, cumulative=False, histtype='bar')
	ax.grid(True)
	ax.xaxis_date()
	plt.setp( ax.get_xticklabels(), rotation=90, horizontalalignment='center', fontsize=8 )
	ax.set_ylabel(ylabel)
	ax.xaxis.set_major_locator(x_locator)
	ax.xaxis.set_major_formatter(x_formatter)
	ax.set_xlim(snum, enum)
	return

#################################
# main program
#################################
# open the origin table
dbpath = '/Seis/Kiska4/picks/Total/Total'
db = datascope.dbopen( dbpath, 'r')
db = db.lookup( table = 'origin' )

# create the figure canvas
fig1 = plt.figure()
fig1.suptitle("db: " + dbpath)
secsperday = 60 * 60 * 24
daysperweek = 7
daysperyear = 365
epochnow = datascope.stock.now()
epochtodaystart = (epochnow // secsperday) * secsperday
epochtodayend = epochtodaystart + secsperday
enum = epoch2num(epochtodayend)
epoch1yearago = epochtodaystart - (secsperday * daysperyear)
epoch1weekago = epochtodaystart - (secsperday * daysperweek)
snum1weekago = epoch2num(epoch1weekago)
snum1yearago = epoch2num(epoch1yearago)

### Last week plot
subset_expr = "ml > -2 && time > " + str(epoch1weekago)
dictorigin = dict();
dictorigin = dbgetorigins(db, subset_expr)
ax1 = fig1.add_subplot(221)
plot_time_ml(ax1, dictorigin, mpl.dates.DayLocator(), mpl.dates.DateFormatter('%d\n%b'), snum1weekago, enum)
ax2 = fig1.add_subplot(222)
plot_binnedtime_counts(ax2, dictorigin, mpl.dates.DayLocator(), mpl.dates.DateFormatter('%d\n%b'), 1.0, 'eqs per day', snum1weekago, enum)

### Last year plot
subset_expr = "ml > -2 && time > " + str(epoch1yearago)
dictorigin = dict();
dictorigin = dbgetorigins(db, subset_expr)
ax3 = fig1.add_subplot(223)
plot_time_ml(ax3, dictorigin, mpl.dates.MonthLocator(), mpl.dates.DateFormatter('%b\n%Y'), snum1yearago, enum)
ax4 = fig1.add_subplot(224)
plot_binnedtime_counts(ax4, dictorigin, mpl.dates.MonthLocator(), mpl.dates.DateFormatter('%b\n%Y'), 7.0, 'eqs per week', snum1yearago, enum)

# close the database
db.free()
db.close()

# save the figure to file
fig1.savefig('plots/counts.png', dpi=130)
