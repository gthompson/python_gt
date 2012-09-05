#!/opt/antelope/python2.7.2-64/bin/python
###############################
#a GT ANTELOPE OBSPY HEADER
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

# note that global/default mpl settings can be given in config files at the global, user home and pwd levels - see p44

# END OF GT ANTELOPE-OBSPY HEADER
#################################

# open the origin table
dbpath = '/Seis/Kiska4/picks/Total/Total'
db = datascope.dbopen( dbpath, 'r')
db = db.lookup( table = 'origin' )

# create the figure canvas
fig1 = plt.figure()
fig1.suptitle("db: " + dbpath)


#####################
###### last week plot
ax1 = fig1.add_subplot(211)

# get the data
subset_expr = "ml > -2 && time > \"2012/07/30\""
db1 = db.subset(subset_expr)
n = db1.nrecs()
print "Events in last week: {}".format(n)
# if size of arrays already known, preallocation much faster than recreating each time with append
origin1_id = np.empty(n)
origin1_ml = np.empty(n)
origin1_epoch = np.empty(n)
origin1_datetime = np.empty(n)
for db1[3] in range(n):
	(origin1_id[db1[3]],origin1_ml[db1[3]],origin1_epoch[db1[3]]) = db1.getv('orid','ml','time')
#db1.free()
#db1.close()
origin1_datetime = mpl.dates.epoch2num(origin1_epoch)

# plot the data
ax1.plot_date(origin1_datetime, origin1_ml, linestyle='.')
ax1.grid(True)
ax1.set_title("Last week")
#ax1.set_xlabel('Date')
ax1.set_ylabel('Ml')
daysLoc = mpl.dates.DayLocator()
daysFmt = mpl.dates.DateFormatter('%d-%b')
ax1.xaxis.set_major_formatter(daysFmt)
##################

#####################
###### last year plot
ax2 = fig1.add_subplot(212)

# get the data
subset_expr = "ml > -2 && time > \"2011/08/07\""
db2 = db.subset(subset_expr)
n = db2.nrecs()
print "Events in last year: {}".format(n)
# if size of arrays already known, preallocation much faster than recreating each time with append
origin2_id = np.empty(n)
origin2_ml = np.empty(n)
origin2_epoch = np.empty(n)
origin2_datetime = np.empty(n)
for db2[3] in range(n):
	(origin2_id[db2[3]],origin2_ml[db2[3]],origin2_epoch[db2[3]]) = db2.getv('orid','ml','time')
#db2.free()
#db2.close()
origin2_datetime = mpl.dates.epoch2num(origin2_epoch)

# plot the data
ax2.plot_date(origin2_datetime, origin2_ml, linestyle='.')
ax2.grid(True)
#ax2.set_title("Last year")
ax2.set_xlabel('Date')
ax2.set_ylabel('Ml')
monthsLoc = mpl.dates.MonthLocator()
monthsFmt = mpl.dates.DateFormatter('%b')
ax2.xaxis.set_major_formatter(monthsFmt)
##################
fig1.autofmt_xdate()
fig1.savefig('plots/counts.png', dpi=130)

db.free()
db.close()
