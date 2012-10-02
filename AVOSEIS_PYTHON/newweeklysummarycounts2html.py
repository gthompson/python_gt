#!/opt/antelope/python2.7.2-64/bin/python
import os, sys
sys.path.append(os.environ['ANTELOPE'] + "/data/python")
import antelope.datascope as datascope
import matplotlib as mpl
import numpy as np
if 'DISPLAY' in os.environ.keys():
	mpl.use("Agg")
import matplotlib.pyplot as plt
import getopt
import modgiseis as giseis
# note that global/default mpl settings can be given in config files at the global, user home and pwd levels - see p44

def usage():
  	print 'Usage: '+sys.argv[0]+' -i <inputeventdb> -o <outputimagefile> [-s <subset_expr>]'
	print """
	where subset_expr is an optional Datascope subset expression 
	Note: your database must have an origin and event table present"""
	print """\nExample: 
	plot all earthquakes from the AVO catalog with Ml>=1.0 within 20km of Iliamna since 1994/01/01\n
	%s -i /Seis/Kiska4/picks/Total/Total -o iliamna_energy.png -s 'ml >= 1.0 && time > \"1994/01/01\" && deg2km(distance(lat, lon, 60.0319, -153.0918))<20.0'
	""" % (sys.argv[0])

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

def main(argv=None):
	try:
    		opts, args = getopt.getopt(argv, 'i:d:v', ['inputdb=', 'description='])
    		if not opts:
      			usage()
  	except getopt.GetoptError,e:
    		print e
    		usage()
    		sys.exit(2)

	verbose = False
	inputdb = None
	description = None
	htmldir = None
	for o, a in opts:
        	if o == "-v":
            		verbose = True
        	elif o in ("-h", "--help"):
            		usage()
            		sys.exit()
        	elif o in ("-i", "--inputdb"):
            		dbpath = a
			if not(os.path.isfile(dbpath)):
			        sys.exit("%s not found" % dbpath)
			if not(os.path.isfile(dbpath + ".origin")):
			        sys.exit("%s.origin not found" % dbpath)

        	elif o in ("-d", "--description"):
            		description = a
			# form an output directory for HTML content and plots from the catalog description
			import re
				htmldir = os.environ['INTERNALWEBPRODUCTS'] + "/counts/" + re.sub(r'\s', '', catalog_description)
				if not(os.path.isdir(htmldir)):
        				try:
                				os.makedirs(htmldir)
        				except:
                				sys.exit("Could not make directory %s" % htmldir)

        	else:
            		assert False, "unhandled option"

	if verbose:
		print "dbpath = " + dbpath
		print "description = " + description

	######## LOAD THE EVENTS 
	# load events from the database dbpath, and apply subset_expr if there is one
	dictorigin = dict();
	dictorigin, numevents = giseis.dbgetorigins(dbpath, subset_expr)

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

	        ### Last week plot
	        print "- Last week plot"
	        subset_expr = radius_expr + " && ml > -2 && time > " + str(epoch1weekago)
	        print "- subsetting with\n\t" + subset_expr
	        dictorigin = dict();
      		dictorigin, n_week[record['place']] = dbgetorigins(db, subset_expr)
        	if n_week[record['place']] > 0:
			binsize = 1.0
                        #locator = mpl.dates.AutoDateLocator()
                        locator = mpl.dates.DayLocator()
                        #formatter = mpl.dates.AutoDateFormatter(locator)
                        formatter = mpl.dates.DateFormatter('%d\n%b')
			bin_edges = np.arange(snum1weekago, enum, binsize)
        	        ax1 = fig1.add_subplot(221)
        	        giseis.plot_time_ml(ax1, dictorigin, locator, formatter, snum1weekago, enum)
        	        ax2 = fig1.add_subplot(222)
        	        giseis.plot_counts(ax2, dictorigin, locator, formatter, bin_edges, snum1weekago, enum)
	
	        ### Last year plot
	        print "- Last year plot"
	        subset_expr = radius_expr + " && ml > -2 && time > " + str(epoch1yearago)
	        print "- subsetting with\n\t" + subset_expr
	        dictorigin = dict();
	        dictorigin, n_year[record['place']] = dbgetorigins(db, subset_expr)
	        if n_year[record['place']] > 0:
			binsize = 7.0
	                #locator = mpl.dates.AutoDateLocator()
	                locator = mpl.dates.MonthLocator()
                	#formatter = mpl.dates.AutoDateFormatter(locator)
			formatter = mpl.dates.DateFormatter('%b\n%Y')
			bin_edges = np.arange(snum1yearago, enum, binsize)
                	ax3 = fig1.add_subplot(223)
                	giseis.plot_time_ml(ax3, dictorigin, locator, formatter, snum1yearago, enum)
                	ax4 = fig1.add_subplot(224)
                	giseis.plot_counts(ax4, dictorigin, locator, formatter, bin_edges, snum1yearago, enum)

                	# save the figure to file
                	supertitle = record['place'] + "(week=" + str(n_week[record['place']]) + ", year=" + str(n_year[record['place']]) + ")"
                	supertitle += "\nLast updated: " + mpl.dates.num2date(numnow).strftime("%Y-%m-%d %H:%M:%S")
                	fig1.suptitle(supertitle)
                	outfile = "%s/counts_%s" % (htmldir, record['place'] + ".png")
                	print "- saving to " + outfile
                	fig1.savefig(outfile, dpi=130)

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


if __name__ == "__main__":
    	main(sys.argv[1:])
