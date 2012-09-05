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

# note that global/default mpl settings can be given in config files at the global, user home and pwd levels - see p44

# END OF GT ANTELOPE-OBSPY HEADER
#################################
# subroutines
#################################

def dbgetorigins(dborigin, subset_expr):
	# load origins from database
	dbptr = dborigin.subset(subset_expr)
	n = dbptr.nrecs()
	print "- number of events = {}".format(n)

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
	return dictorigin, n

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

def read_volcanoes():
	dbplacespath = 'volcanoes'
	dbhandle = datascope.dbopen( dbplacespath, 'r')
	dbptr = dbhandle.lookup( table = 'places' )
	n = dbptr.nrecs()
	dictplaces = dict()
	for dbptr[3] in range(n):
		thisrecord = {'place': "%s" % dbptr.getv('place'), 'lat': "%s" % dbptr.getv('lat'), 'lon': "%s" % dbptr.getv('lon') }
		dictplaces[dbptr[3]] =  thisrecord
	dbhandle.free()
	dbhandle.close()
	return dictplaces

def write_counts_to_html(n, catalog_description, timeperiod):
	html_string = ""
	html_string += "<h3>Earthquake counts for the past %s, from the %s</h3>" % (timeperiod, catalog_description)


	# start table here
	html_string += "<table border=1>"
	html_string += "<tr><th>Rank</th><th>Place</th><th># earthquakes</th></tr>"

	# reverse sort the last week counts	
	lastvalue = 999999 # dummy value
	rank = 1
	thisrung = ""
	thisrungitems = 0
	firsttime = True
	for key, value in sorted(n.iteritems(), key=lambda (k,v): (v, k), reverse=True):
		print "%s, %d" % (key, value)
		if value==lastvalue: 
			if value==0:
				thisrung = thisrung + ", " + key
			else:
				thisrung = thisrung + ", <a href=counts_" + key + ".png >" + key + "</a>"
			thisrungitems += 1
		else:
			if firsttime==True:
				firsttime = False
			else:
				html_string += "<tr><td>%d</td><td>%s</td><td>%d</td></tr>" % (rank, thisrung, lastvalue)
			rank += thisrungitems
			if value==0:
				thisrung = key
			else:
				thisrung = "<a href=counts_" + key + ".png >" + key + "</a>"
			thisrungitems = 1
		lastvalue = value


	# end table here
	html_string += "</table>"
	html_string += "<b>No earthquakes at:</b> %s\n" %thisrung


	return html_string

#################################
# main program
#################################

# get command line arguments
if len(sys.argv) != 3:
        # stop program and print an error message
        sys.exit("Usage: %s /path/to/database description\ne.g.\n\t%s /Seis/Kiska4/picks/Total/Total 'AVO analyst-reviewed catalog'" % (sys.argv[0], sys.argv[0]))
dbpath = sys.argv[1]
if not(os.path.isfile(dbpath)):
	sys.exit("%s not found" % dbpath)
if not(os.path.isfile(dbpath + ".origin")):
	sys.exit("%s.origin not found" % dbpath)
catalog_description = sys.argv[2]

# form an output directory for HTML content and plots from the catalog description
import re
htmldir = os.environ['INTERNALWEBPRODUCTS'] + "/counts/" + re.sub(r'\s', '', catalog_description)
if not(os.path.isdir(htmldir)):
	try:
		os.makedirs(htmldir)
	except:
		sys.exit("Could not make directory %s" % htmldir)


# open the origin table
db = datascope.dbopen( dbpath, 'r')
db = db.lookup( table = 'origin' )

# read the dict of places
dictplaces = dict()
dictplaces = read_volcanoes()
n_week = dict()
n_year = dict()
RADIUS_IN_KM = 25.0

for index in dictplaces.keys():
	record = dictplaces[index]
	print "\nProcessing " + record['place'] + ":"
	radius_expr = "deg2km(distance(lat, lon, " + record['lat'] + ", " + record['lon'] + ")) < %f" % RADIUS_IN_KM

	# create the figure canvas
	fig1 = plt.figure()

	secsperday = 60 * 60 * 24
	daysperweek = 7
	daysperyear = 365
	epochnow = datascope.stock.now()
	numnow = mpl.dates.epoch2num(epochnow)
	epochtodaystart = (epochnow // secsperday) * secsperday
	epochtodayend = epochtodaystart + secsperday
	enum = mpl.dates.epoch2num(epochtodayend)
	epoch1yearago = epochtodaystart - (secsperday * daysperyear)
	epoch1weekago = epochtodaystart - (secsperday * daysperweek)
	snum1weekago = mpl.dates.epoch2num(epoch1weekago)
	snum1yearago = mpl.dates.epoch2num(epoch1yearago)

	### Last week plot
	print "- Last week plot"
	subset_expr = radius_expr + " && ml > -2 && time > " + str(epoch1weekago)
	print "- subsetting with\n\t" + subset_expr
	dictorigin = dict();
	dictorigin, n_week[record['place']] = dbgetorigins(db, subset_expr)
	if n_week[record['place']] > 0:
		ax1 = fig1.add_subplot(221)
		plot_time_ml(ax1, dictorigin, mpl.dates.DayLocator(), mpl.dates.DateFormatter('%d\n%b'), snum1weekago, enum)
		ax2 = fig1.add_subplot(222)
		plot_binnedtime_counts(ax2, dictorigin, mpl.dates.DayLocator(), mpl.dates.DateFormatter('%d\n%b'), 1.0, 'eqs per day', snum1weekago, enum)

	### Last year plot
	print "- Last year plot"
	subset_expr = radius_expr + " && ml > -2 && time > " + str(epoch1yearago)
	print "- subsetting with\n\t" + subset_expr
	dictorigin = dict();
	dictorigin, n_year[record['place']] = dbgetorigins(db, subset_expr)
	if n_year[record['place']] > 0:
		ax3 = fig1.add_subplot(223)
		plot_time_ml(ax3, dictorigin, mpl.dates.MonthLocator(), mpl.dates.DateFormatter('%b\n%Y'), snum1yearago, enum)
		ax4 = fig1.add_subplot(224)
		plot_binnedtime_counts(ax4, dictorigin, mpl.dates.MonthLocator(), mpl.dates.DateFormatter('%b\n%Y'), 7.0, 'eqs per week', snum1yearago, enum)

		# save the figure to file
		supertitle = record['place'] + "(week=" + str(n_week[record['place']]) + ", year=" + str(n_year[record['place']]) + ")" 
		supertitle += "\nLast updated: " + mpl.dates.num2date(numnow).strftime("%Y-%m-%d %H:%M:%S")
		fig1.suptitle(supertitle)
		outfile = "%s/counts_%s" % (htmldir, record['place'] + ".png")
		print "- saving to " + outfile
		fig1.savefig(outfile, dpi=130)

# close the database
db.free()
db.close()

# write HTML header
html_string = ""
html_string += "<html>"
html_string += "<head>"
html_string += "<title>Weekly seismicity review page</title>"
html_string += "</head>"
html_string += "<body>"

# write HTML body - the complicated part
html_string += write_counts_to_html(n_week, catalog_description, "week")
html_string += write_counts_to_html(n_year, catalog_description, "year")

# write HTML footer
html_string += "<hr/><br/>Counts reported are the number of earthquakes within %.0f km of the coordinates given at <a href=http://www.avo.alaska.edu/volcanoes/latlong.php >http://www.avo.alaska.edu/volcanoes/latlong.php</a>." % RADIUS_IN_KM 
html_string += "<br/><em>Last run at %s</em>" % mpl.dates.num2date(numnow).strftime("%Y-%m-%d %H:%M:%S")
html_string += "</body>"
html_string += "</html>"

# write to file
fileptr = open("%s/index.html" % htmldir, "w")
fileptr.write(html_string)
fileptr.close()
