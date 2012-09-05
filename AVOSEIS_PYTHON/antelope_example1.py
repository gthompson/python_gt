#!/opt/antelope/python2.7.2-64/bin/python
import os, sys
sys.path.append(os.environ['ANTELOPE'] + "/data/python")
import antelope.datascope as datascope
import numpy as np

# command line arguments
if len(sys.argv) < 2:
        # stop program and print a usage message
        sys.exit("Not enough arguments")
dbpath = sys.argv[1]
if not(os.path.isfile(dbpath)):
	sys.exit("%s not found" % dbpath)
subset_expr = ""
if len(sys.argv) > 2:
	subset_expr = sys.argv[2] # expression to use when subsetting database

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

# close the database
db.free()
db.close()

