#!/opt/antelope/python2.7.2-64/bin/python
##### THIS IS A GOOD HEADER TO USE FOR ANTELOPE-MATPLOTLIB TOOLS
import os, sys
sys.path.append(os.environ['ANTELOPE'] + "/data/python")
sys.path.append('~/src/python_gt/AVOSEIS_PYTHON')
import antelope.datascope as datascope
import matplotlib as mpl
if 'DISPLAY' in os.environ.keys():
        mpl.use("Agg")

#################################
# main program
#################################
import modgiseis
import dbploteventrate
import time
import datetime

# time now
datetimenow = datetime.datetime.now() # datetime
epochnow2 = datascope.stock.now() # epoch
epochnow = time.mktime(datetimenow.timetuple()) # epoch
numnow = mpl.dates.epoch2num(epochnow) # datenumber
print "epochdiff = %f " % (epochnow - epochnow2) 

# epoch at start and end today
secsperday = 60 * 60 * 24
daysperyear = 365
dayspermonth = 30
epochtodaystart = (epochnow // secsperday) * secsperday
epochtodayend = epochtodaystart + secsperday

# datenum start and end time
enum = mpl.dates.epoch2num(epochtodayend)
epoch1yearago = epochtodaystart - (secsperday * daysperyear)
epoch1monthago = epochtodaystart - (secsperday * dayspermonth)
snum1yearago = mpl.dates.epoch2num(epoch1yearago)
snum1monthago = mpl.dates.epoch2num(epoch1monthago)

catalogpath = '/Seis/Kiska4/picks/Total/Total'
dbplacespath = "/usr/local/mosaic/AVO/internal/avoseis/dev/data/places/volcanoes"
#outdir = "/usr/local/mosaic/AVO/internal/avoseis/dev/counts"
outdir = "/usr/local/mosaic/AVO/avoseis/counts"
htmlfile = "/usr/local/mosaic/AVO/internal/avoseis/dev/counts/index.html"
dictplaces = modgiseis.readplacesdb(dbplacespath)
place = dictplaces['place']
lat = dictplaces['lat']
lon = dictplaces['lon']
n = place.__len__()
html_str = "<html><head><title>Earthquake Counts Menu</title></head><body>\n"
if n > 0:
	print "- number of places = {}".format(n)

	for c in range(n):

		# LAST MONTH
		monthfile = outdir + "/" + place[c] + "_month.png"
		if os.path.exists(monthfile):
			os.remove(monthfile)
		subset_expr = "time > %f && deg2km(distance(lat, lon, %s, %s))<20.0" % (epoch1monthago, lat[c], lon[c])
		dbploteventrate.main([catalogpath, monthfile, subset_expr, snum1monthago, enum])


		# LAST YEAR
		yearfile = outdir + "/" + place[c] + "_year.png"
		if os.path.exists(yearfile):
			os.remove(yearfile)
		subset_expr = "time > %f && deg2km(distance(lat, lon, %s, %s))<20.0" % (epoch1yearago, lat[c], lon[c])
		dbploteventrate.main([catalogpath, yearfile, subset_expr, snum1yearago, enum])

		# TOTAL
		totalfile = outdir + "/" + place[c] + "_total.png"
		if os.path.exists(totalfile):
			os.remove(totalfile)
		subset_expr = "deg2km(distance(lat, lon, %s, %s))<20.0" % (lat[c], lon[c])
		dbploteventrate.main([catalogpath, totalfile, subset_expr])

		if os.path.exists(totalfile):
			html_str += place[c] + ":&nbsp;"
			if os.path.exists(monthfile):
				html_str += "<a href=" + os.path.basename(monthfile) + ">month</a>&nbsp;"
			if os.path.exists(yearfile):
				html_str += "<a href=" + os.path.basename(yearfile) + ">year</a>&nbsp;"
			html_str += "<a href=" + os.path.basename(totalfile) + ">all</a><br/>\n"
html_str += "</body></html>\n"
fo = open(htmlfile, "wb")
fo.write( html_str );
fo.close()
print "Done.\n"

