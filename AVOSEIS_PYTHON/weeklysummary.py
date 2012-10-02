#!/opt/antelope/python2.7.2-64/bin/python
import os, sys
sys.path.append(os.environ['ANTELOPE'] + "/data/python")
sys.path.append('~/src/python_gt/AVOSEIS_PYTHON')
import antelope.datascope as datascope
import numpy as np
import matplotlib as mpl
if 'DISPLAY' in os.environ.keys():
        mpl.use("Agg")
import matplotlib.pyplot as plt
import modgiseis
import time
import datetime
import getopt
######################################################
# trim whitespace from the image file
from PIL import Image, ImageChops

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

def usage():
        print 'Usage: '+sys.argv[0]+' <catalogpath> <dbplacespath> <outputdir> <number_of_weeks_to_plot> <weeksagofilter>'
        print """
        <catalogpath> must have an origin and event table present
        <dbplacespath> is a list of volcanoes and their lat, lon, elev and radii in places_avo_1.3 schema format
	"""
        print """\nExample: 
        produce a weekly summary the AVO catalog for all volcanoes with an earthquake in the past 1 week \n
        %s /Seis/Kiska4/picks/Total/Total volcanoes_avo /usr/local/mosaic/AVO/avoseis/counts 13 1
        """ % (sys.argv[0])


def y2percentile(y, thesepercentiles):
	notfound = True
	index = -1
	p = 100
	while notfound and index<100:
		index += 1
		#print index, thesepercentiles[index], y, thesepercentiles[index]>y
		if thesepercentiles[index] >= y:
			p = index
			notfound = False
	return p

def print_pixels(fighandle, axhandle, number_of_weeks_to_plot, NUMVOLCANOES):
	dpi = fighandle.get_dpi()
	sizeInInches = fighandle.get_size_inches()
	print "Figure Inches: %f x %f" % (sizeInInches[0], sizeInInches[1])
	print "dpi: %d" % dpi
	print "Figure Pixels: %f x %f" % (sizeInInches[0] * dpi, sizeInInches[1] * dpi)
	posbbox = axhandle.get_position()
	posbbox = posbbox.get_points()
	print posbbox
	pos = np.empty(4)
	pos[0] = posbbox[0][0]
	pos[1] = posbbox[0][1]
	pos[2] = posbbox[1][0] - pos[0]
	pos[3] = posbbox[1][1] - pos[1]
	print pos
	print "Axes Position: %f to %f x %f to %f" % (posbbox[0][0], posbbox[1][0], posbbox[0][1], posbbox[1][1])
	axeswidthinpixels = pos[2]*dpi*sizeInInches[0]
	axesheightinpixels = pos[3]*dpi*sizeInInches[1]
	print 'Axes size in pixels: %f x %f' % (axeswidthinpixels, axesheightinpixels)
	gridwidthinpixels = axeswidthinpixels / (NUMVOLCANOES + 1)
	gridheightinpixels = axesheightinpixels / (number_of_weeks_to_plot + 1)
	print 'Grid size in pixels: %f x %f' % (gridwidthinpixels, gridheightinpixels)

def main(argv=None):
        try:
                opts, args = getopt.getopt(argv, 'vh')
                if len(args)<5:
                        usage()
                        sys.exit(2)
                catalogpath = args[0]
                dbplacespath = args[1]
                outdir = args[2]
		number_of_weeks_to_plot = int(args[3])
		weeksagofilter = int(args[4])
        except getopt.GetoptError,e:
                print e
                usage()
                sys.exit(2)

        verbose = False

        for o, a in opts:
                if o == "-v":
                        verbose = True
                elif o in ("-h", "--help"):
                        usage()
                        sys.exit()
                else:
                        assert False, "unhandled option"

        if verbose:
                print "catalogpath = " + catalogpath
                print "dbplacespath = " + dbplacespath
                print "outdir = " + outdir
                print "number_of_weeks_to_plot = %d" % number_of_weeks_to_plot
		print "weeksagofilter = %d" % weeksagofilter

	# time now
	datetimenow = datetime.datetime.now() # datetime
	#epochnow = time.mktime(datetimenow.timetuple()) # epoch
	epochnow = datascope.stock.now()
	datenumnow = mpl.dates.epoch2num(epochnow) # datenumber
	secsperday = 60 * 60 * 24
	epochfilter = epochnow - (secsperday * 7 * weeksagofilter)
	epoch1989 = 599616000

	dictplaces = modgiseis.readplacesdb(dbplacespath)
	place = dictplaces['place']
	lat = dictplaces['lat']
	lon = dictplaces['lon']
	radius = dictplaces['radius']
	n = place.__len__()
	VOLCANO = list()
	BIN_EDGES = list()
	COUNTS = list()
	CUMML = list()


	if n > 0:
		print "- number of places = {}".format(n)
	
		for c in range(n): # for each volcano in the list
			nfilter = 0
				
			print "PROCESSING %s" % place[c]

			# how many earthquakes have there been in the last week?
			subset_expr = "time > %f && deg2km(distance(lat, lon, %s, %s))<%f" % (epochfilter, lat[c], lon[c], float(radius[c]))
			dictorigin, nfilter = modgiseis.dbgetorigins(catalogpath, subset_expr)
	
			# load all time history and bin them 
			if (nfilter > 0):
				subset_expr = "time > %f && deg2km(distance(lat, lon, %s, %s))<%f" % (epoch1989, lat[c], lon[c], float(radius[c]))
				print "'%s'" % subset_expr
	                	dictorigin, n = modgiseis.dbgetorigins(catalogpath, subset_expr)
				print "- number of events in all-time = {}".format(n)
				time = dictorigin['time']
				time_firstevent = time[0] # assuming they are sorted
				if verbose:
					print 'firstevent: %s' % modgiseis.datenum2datestr(time_firstevent)
					print 'lastevent: %s' % modgiseis.datenum2datestr(time[-1])
				bin_edges, snum, enum = modgiseis.compute_bins(dictorigin, time_firstevent, datenumnow, 7.0) # function name is a misnomer - we are computing bin_edges
	
				# now we get our array of counts per week
				counts = modgiseis.bin_counts(dictorigin['time'], bin_edges)
	        		energy = modgiseis.ml2energy(dictorigin['ml'])
	        		binned_energy = modgiseis.bin_irregular(dictorigin['time'], energy, bin_edges)
				binned_ml = modgiseis.energy2ml(binned_energy)
	
				if verbose:
					for index in [0, -2, -1]:
						print 'edge %d: %s' % (index, modgiseis.datenum2datestr(bin_edges[index]))
				VOLCANO.append(place[c])
				BIN_EDGES.append(bin_edges)
				COUNTS.append(counts)
				CUMML.append(binned_ml)
	
	# Great we have our data in 3 convenient Python lists. 
	# VOLCANO is a list of strings
	# BIN_EDGES and COUNTS are lists of numpy arrays (one per volcano)
	if verbose:
		print VOLCANO
		print len(VOLCANO)
		print len(BIN_EDGES)
		print len(COUNTS)
		print len(CUMML)
	
	# Now lets do something with these data
	# Lets work out our distributions
	NUMVOLCANOES = len(VOLCANO)
	y = np.empty(NUMVOLCANOES)
	PERCENTILES = list()
	percentages = range(101)
	for i in range(NUMVOLCANOES):
		#thesecounts = COUNTS[i-1]
		thesecounts = COUNTS[i]
		thesepercentiles = np.empty(101)
		thesepercentiles = np.percentile(thesecounts, percentages)
		PERCENTILES.append(thesepercentiles)
	
	 
	# Prototype A - a web page with a bar chart of counts this week vs. volcano
	# A1: first lets produce the figure
	NUMVOLCANOES = len(VOLCANO)
	y = np.empty(NUMVOLCANOES)
	p = np.empty(NUMVOLCANOES)
	for i in range(NUMVOLCANOES):
		print "Percentiles for %s" % VOLCANO[i]
		thesecounts = COUNTS[i]
		y[i] = thesecounts[-1]
		p[i] = y2percentile(y[i],PERCENTILES[i])
		
	fig1 = plt.figure()
	
	fig1ax1 = fig1.add_subplot(211)
	fig1ax1.bar(range(NUMVOLCANOES),y,width=1)
	fig1ax1.set_xticks(np.arange(.5,NUMVOLCANOES+.5,1))
	fig1ax1.set_xticklabels(VOLCANO)
	fig1ax1.set_ylabel('Counts')
	plt.setp( fig1ax1.get_xticklabels(), rotation=45, horizontalalignment='right', fontsize=7 )
	
	fig1ax2 = fig1.add_subplot(212)
	fig1ax2.bar(range(NUMVOLCANOES),p,width=1)
	fig1ax2.set_xticks(np.arange(.5,NUMVOLCANOES+.5,1))
	fig1ax2.set_xticklabels(VOLCANO)
	fig1ax2.set_ylabel('Percentile')
	plt.setp( fig1ax2.get_xticklabels(), rotation=45, horizontalalignment='right', fontsize=7 )
	
	fig1.suptitle('AVO earthquakes in the past week')
	fig1.savefig("%s/prototypeA2.png" % outdir, dpi=130)
	
	# Prototype B - weeks ago versus volcano
	
	weeksago = range(number_of_weeks_to_plot+1)
	fig2 = plt.figure()
	if number_of_weeks_to_plot > NUMVOLCANOES:
		dpi = 6*(number_of_weeks_to_plot+1)
	else:
		dpi = 6*(NUMVOLCANOES+1)
	fig2.set_dpi(dpi)
	fig2.set_size_inches((10.0,10.0),forward=True)
	#axes_width = 0.8 * (NUMVOLCANOES + 1) / 52
	#axes_height = 0.8 * (number_of_weeks_to_plot + 1) / 52
	if number_of_weeks_to_plot > NUMVOLCANOES:
		axes_width = 0.8 * (NUMVOLCANOES + 1) / (number_of_weeks_to_plot + 1)
		axes_height = 0.8
	else:
		axes_width = 0.8
		axes_height = 0.8 * (number_of_weeks_to_plot + 1) / (NUMVOLCANOES + 1)
	fig2ax1 = fig2.add_axes([0.1, 0.85-axes_height, axes_width, axes_height])
	print_pixels(fig2, fig2ax1, number_of_weeks_to_plot, NUMVOLCANOES)
	
	import matplotlib.cm as cmx
	import matplotlib.colors as colors
	RdYlGn = cm = plt.get_cmap('RdYlGn_r')
	cNorm = colors.Normalize(vmin=1.0, vmax=4.0)
	scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=RdYlGn)
	#print scalarMap.get_clim()
	volcanolabels = list()
	SCALEFACTOR = 84.0 / dpi
	#MAXMARKERSIZE = 38.4
	MAXMARKERSIZE = 41.0 * SCALEFACTOR
	MINMARKERSIZE = 2.0 * SCALEFACTOR
	PTHRESHOLD = 50
	weekending = list()
	for i in range(NUMVOLCANOES):
		thesecounts = COUNTS[i]
		thesecumml = CUMML[i]
		volcanolabels.append("%s(%d)" % (VOLCANO[i], thesecounts[-1]))
	
		#for weeksago in range(number_of_weeks_to_plot+1):
		for week in weeksago:
			if i==0:
				dstr = modgiseis.datenum2datestr(bin_edges[-1-week])
				print week, dstr
				weekending.append(dstr[5:10])
			y = thesecounts[-(week+1)]
			magnitude = thesecumml[-(week+1)]
			p = y2percentile(y,PERCENTILES[i])
			if y>0:
				#colorVal = scalarMap.to_rgba(p)
				colorVal = scalarMap.to_rgba(magnitude)
				msize = MINMARKERSIZE + (p-PTHRESHOLD) * (MAXMARKERSIZE - MINMARKERSIZE) / (100-PTHRESHOLD)
				if msize<MINMARKERSIZE:
					msize=MINMARKERSIZE
				#fig2ax1.plot(i+0.5,-week,'o',color=colorVal,markersize=msize );
				fig2ax1.plot(i+0.5,-week,'s',color=colorVal,markersize=msize,linewidth=0 );
				if msize > MAXMARKERSIZE * 0.3:
					fig2ax1.text(i+0.5, -week, "%d" % y, horizontalalignment='center', verticalalignment='center', fontsize = 8 * SCALEFACTOR)
	fig2ax1.set_axisbelow(True)
	
	fig2ax1.set_xticks(np.arange(.5,NUMVOLCANOES+.5,1))
	fig2ax1.set_xlim([-0.5, NUMVOLCANOES+0.5])
	#fig2ax1.set_yticks(np.arange(-weeksago[-1], weeksago[0], 1))
	fig2ax1.set_yticks(0.5+np.arange(-number_of_weeks_to_plot, 0+1, 1))
	fig2ax1.set_yticklabels(weekending[::-1])
	#fig2ax1.grid(True)
	#fig2ax1.yaxis.grid(False)
	fig2ax1.xaxis.grid(True, linestyle='-', color='gray')
	#fig2ax1.set_xticklabels(VOLCANO)
	fig2ax1.set_xticklabels(volcanolabels)
	timenowstr = datetimenow.strftime('%Y/%m/%d %H:%M:%S')
	
	
	fig2ax1.set_ylim([-weeksago[-1]-0.5, weeksago[0]+0.5])
	fig2ax1.xaxis.set_ticks_position('top')
	fig2ax1.xaxis.set_label_position('top')
	plt.setp( fig2ax1.get_xticklabels(), rotation=45, horizontalalignment='left', fontsize=10*SCALEFACTOR )
	plt.setp( fig2ax1.get_yticklabels(), fontsize=10*SCALEFACTOR )
	outfile = "%s/weeklysummary.png" % outdir
	fig2.savefig(outfile, dpi=dpi)
	
	# Legend for prototype B
	fig3 = plt.figure()
	fig3.set_dpi(dpi)
	fig3.set_size_inches((10.0,10.0),forward=True)
	fig3ax2 = fig3.add_axes([0.1, 0.85-axes_height/2, axes_width/20, axes_height/2])
	#fig3ax2 = fig3.add_axes([0.88, 0.4, 0.03, 0.4])
	a = np.linspace(0, 1, 256).reshape(-1,1)
	fig3ax2.imshow(a, aspect='auto', cmap=plt.get_cmap('RdYlGn_r'), origin='lower')
	fig3ax2.set_xticks([])
	fig3ax2.set_yticks(np.arange(0,256+1,256/6)) # the +1 is to label the top of the range since arange stops at 256-51.2 otherwise
	#fig3ax2.set_yticklabels(['<=50', '60', '70', '80', '90', '100'])
	fig3ax2.set_yticklabels(['<=1.0', '1.5', '2.0', '2.5', '3.0', '3.5', '4.0'])
	#fig3ax2.set_ylabel('Percentile')
	fig3ax2.set_ylabel('Cumulative\nMagnitude')
	fig3.savefig("%s/weeklysummary_colorbar.png" % outdir, dpi=dpi)
	
	
	im = Image.open(outfile)
	im = trim(im)
	im.save(outfile) 
	############
	
	
	print "Done.\n"


if __name__ == "__main__":
        if len(sys.argv) > 1:
                main(sys.argv[1:])
        else:
                usage()
					
