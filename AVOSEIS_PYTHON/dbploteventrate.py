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

def usage():
  	print 'Usage: '+sys.argv[0]+' -i <inputeventdb> -o <outputimagefile> [-s <subset_expr>]'
	print """
	where subset_expr is an optional Datascope subset expression 
	Note: your database must have an origin and event table present"""
	print """\nExample: 
	plot all earthquakes from the AVO catalog with Ml>=1.0 within 20km of Iliamna since 1994/01/01\n
	%s -i /Seis/Kiska4/picks/Total/Total -o iliamna_energy.png -s 'ml >= 1.0 && time > \"1994/01/01\" && deg2km(distance(lat, lon, 60.0319, -153.0918))<20.0'
	""" % (sys.argv[0])

def main(argv=None):
	try:
    		opts, args = getopt.getopt(argv, 'i:o:s:v', ['input=', 'output=', 'subset_expr='])
    		if not opts:
      			usage()
  	except getopt.GetoptError,e:
    		print e
    		usage()
    		sys.exit(2)

	verbose = False
	inputdb = None
	outfile = None
	subset_expr = None
	for o, a in opts:
        	if o == "-v":
            		verbose = True
        	elif o in ("-h", "--help"):
            		usage()
            		sys.exit()
        	elif o in ("-i", "--inputdb"):
            		dbpath = a
        	elif o in ("-o", "--outfile"):
            		outfile = a
        	elif o in ("-s", "--subset_expr"):
            		subset_expr = a
        	else:
            		assert False, "unhandled option"

	if verbose:
		print "dbpath = " + dbpath
		print "outfile = " + outfile
		print "subset_expr = " + subset_expr

	######## LOAD THE EVENTS 
	# load events from the database dbpath, and apply subset_expr if there is one
	dictorigin = dict();
	dictorigin, numevents = giseis.dbgetorigins(dbpath, subset_expr)

	# if we loaded some events, create plots
	if numevents > 0:

		###### PLOT DATA HERE 

		# Compute bin_edges based on the first and last event times
		bin_edges, snum, enum = giseis.compute_binsize(dictorigin)

		# Let matplotlib automatically decide where to put date (x-axis) tick marks, and what style of labels to use
		locator = mpl.dates.AutoDateLocator()
		formatter = mpl.dates.AutoDateFormatter(locator)

		# create the figure canvas
		fig1 = plt.figure()

		# add subplot - ml versus time
		ax1 = fig1.add_subplot(311)
		giseis.plot_time_ml(ax1, dictorigin, locator, formatter, snum, enum)
	
		# add subplot - counts versus time
		ax2 = fig1.add_subplot(312)
		giseis.plot_counts(ax2, dictorigin, locator, formatter, bin_edges, snum, enum)
	
		# add subplot - energy versus time
		ax3 = fig1.add_subplot(313)
		giseis.plot_energy(ax3, dictorigin, locator, formatter, bin_edges, snum, enum)

		####### SAVE FIGURE

		# save the figure to outfile at 130 dots per inch
		print "- saving to " + outfile
		fig1.savefig(outfile, dpi=130)




if __name__ == "__main__":
    	main(sys.argv[1:])
