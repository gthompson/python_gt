#!/opt/antelope/python2.7.2-64/bin/python
##### THIS IS A GOOD HEADER TO USE FOR ANTELOPE-MATPLOTLIB TOOLS
import os, sys
sys.path.append(os.environ['ANTELOPE'] + "/data/python")
import antelope.datascope as datascope

#################################
# main program
#################################
import giseistools2
import dbploteventrate
import time
import datetime
datetimenow = datetime.datetime.now()
epochnow = time.mktime(datetimenow.timetuple())
epoch_lastweek = epochnow - 7 * 86400
epoch_lastyear = epochnow - 7 * 365

catalogpath = '/Seis/Kiska4/picks/Total/Total'
dbplacespath = "/usr/local/mosaic/AVO/internal/avoseis/dev/data/places/volcanoes"
outdir = "/usr/local/mosaic/AVO/internal/avoseis/dev/counts"
dictplaces = giseistools2.readplacesdb(dbplacespath)
place = dictplaces['place']
lat = dictplaces['lat']
lon = dictplaces['lon']
print place
print lat
print lon
n = place.__len__()
if n > 0:
	print "- number of places = {}".format(n)

	for c in range(n):
		outfile = outdir + "/" + place[c] + "_counts.png"
		subset_expr = "time > %f && deg2km(distance(lat, lon, %s, %s))<20.0" % (epoch_lastweek, lat[c], lon[c])
		print "Calling dbploteventcountsenergy with %s, %s, %s" % (catalogpath, outfile, subset_expr)
		dbploteventrate.main([catalogpath, outfile, subset_expr])

print "Done.\n"

