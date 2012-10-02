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

def print_pixels(fighandle, axhandle, MAXWEEKSAGO, NUMVOLCANOES):
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
	gridheightinpixels = axesheightinpixels / (MAXWEEKSAGO + 1)
	print 'Grid size in pixels: %f x %f' % (gridwidthinpixels, gridheightinpixels)

######################################################
verbose = False

# time now
datetimenow = datetime.datetime.now() # datetime
epochnow = time.mktime(datetimenow.timetuple()) # epoch
datenumnow = mpl.dates.epoch2num(epochnow) # datenumber
secsperday = 60 * 60 * 24
MAXWEEKSAGO =  13
maxweeksagoepoch = epochnow - (secsperday * 7 * MAXWEEKSAGO)
twoweeksagoepoch = epochnow - (secsperday * 14)
epoch1989 = 599616000

#catalogpath = '/Seis/Kiska4/picks/Total/Total'
catalogpath = '/avort/oprun/events/optimised/Total'
dbplacespath = "/usr/local/mosaic/AVO/internal/avoseis/dev/data/places/volcanoes"
#dbplacespath = "volcanoes"
#outdir = "/usr/local/mosaic/AVO/internal/avoseis/dev/counts"
outdir = "/usr/local/mosaic/AVO/avoseis/counts_avortdb"
dictplaces = modgiseis.readplacesdb(dbplacespath)
place = dictplaces['place']
lat = dictplaces['lat']
lon = dictplaces['lon']
n = place.__len__()
#index = 0
VOLCANO = list()
BIN_EDGES = list()
COUNTS = list()
CUMML = list()


if n > 0:
	print "- number of places = {}".format(n)

	for c in range(n): # for each volcano in the list

		print "PROCESSING %s" % place[c]
	
		# how many earthquakes have there been in the last week?
		subset_expr = "time > %f && deg2km(distance(lat, lon, %s, %s))<20.0" % (twoweeksagoepoch, lat[c], lon[c])
		print subset_expr
		dictorigin, n = modgiseis.dbgetorigins(catalogpath, subset_expr)
		print "- number of events in past week = {}".format(n)

		# if > 0, load all time history and bin them 
		if n > 0:
			subset_expr = "time > %f && deg2km(distance(lat, lon, %s, %s))<20.0" % (epoch1989, lat[c], lon[c])
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

			# check again that we really do have events in the last week
			if sum(counts[-2:-1]) > 0:
			#if sum(counts) > 0:
				if verbose:
					for index in [0, -2, -1]:
						print 'edge %d: %s' % (index, modgiseis.datenum2datestr(bin_edges[index]))
				VOLCANO.append(place[c])
				BIN_EDGES.append(bin_edges)
				COUNTS.append(counts)
				CUMML.append(binned_ml)

# Great we have our data in 3 coNUMVOLCANOESenient Python lists. 
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
fig1.savefig("%s/prototypeA.png" % outdir, dpi=130)

# Prototype B - weeks ago versus volcano

weeksago = range(MAXWEEKSAGO+1)
fig2 = plt.figure()
if MAXWEEKSAGO > NUMVOLCANOES:
	dpi = 6*(MAXWEEKSAGO+1)
else:
	dpi = 6*(NUMVOLCANOES+1)
fig2.set_dpi(dpi)
fig2.set_size_inches((10.0,10.0),forward=True)
#axes_width = 0.8 * (NUMVOLCANOES + 1) / 52
#axes_height = 0.8 * (MAXWEEKSAGO + 1) / 52
if MAXWEEKSAGO > NUMVOLCANOES:
	axes_width = 0.8 * (NUMVOLCANOES + 1) / (MAXWEEKSAGO + 1)
	axes_height = 0.8
else:
	axes_width = 0.8
	axes_height = 0.8 * (MAXWEEKSAGO + 1) / (NUMVOLCANOES + 1)
fig2ax1 = fig2.add_axes([0.1, 0.85-axes_height, axes_width, axes_height])
print_pixels(fig2, fig2ax1, MAXWEEKSAGO, NUMVOLCANOES)

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

	#for weeksago in range(MAXWEEKSAGO+1):
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
fig2ax1.set_yticks(0.5+np.arange(-MAXWEEKSAGO, 0+1, 1))
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
outfile = "%s/weekly_report.png" % outdir
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
fig3.savefig("%s/weekly_report_colorbar.png" % outdir, dpi=dpi)


im = Image.open(outfile)
im = trim(im)
im.save(outfile) 
############


print "Done.\n"

