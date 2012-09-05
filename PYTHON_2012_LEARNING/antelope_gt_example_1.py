#!/opt/antelope/python2.7.2-64/bin/python
###############################
#a GT ANTELOPE OBSPY HEADER
import sys, os
sys.path.append(os.environ['ANTELOPE'] + "/data/python")

# OBSPY_EXT by Mark Williams
sys.path.append("/Users/glenn/src/obspy_ext/antelope")
import core

# Stuff in an Antelope-python example
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Antelope stuff
import antelope.datascope as datascope

# numpy & matplotlib
import numpy as np
#import matplotlib.mlab as mlab
#import matplotlib.pyplot as plt
import pylab

# END OF GT ANTELOPE-OBSPY HEADER
#################################

#dbcreate('mydb', 'css3.0', '/opt/antelope/data/db/demo/demo', 'a temporary database created by Glenn', 'Some details about the database')
db = datascope.dbopen( '/opt/antelope/data/db/demo/demo', 'r')
db = db.lookup( table = 'origin' )
#db.subset("ml > 2.0")
n = db.nrecs()
print "Number of records: {}".format(n)
# if size of arrays already known, preallocation much faster than recreating each time with append
orid = np.empty(n)
ml = np.empty(n)
for db[3] in range(n):
	(orid[db[3]],ml[db[3]]) = db.getv('orid','ml')
	#print "{}{}".format(ml,orid)
	#print str(db[3]).rjust(5) + " " + str(ml).rjust(7) + " " + str(orid).rjust(6)
db.free()
db.close()
print ml

import pylab
pylab.plot(ml)
pylab.savefig('myplot.png',dpi=100)
#pylab.show()
# the following does not work on RHEL
os.system("open myplot.png")




