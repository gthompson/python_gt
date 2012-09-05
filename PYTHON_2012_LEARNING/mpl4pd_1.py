#!/opt/antelope/python2.7.2-64/bin/python
###############################
#a GT ANTELOPE OBSPY HEADER
import sys, os
sys.path.append(os.environ['ANTELOPE'] + "/data/python")

# OBSPY_EXT by Mark Williams
#sys.path.append("/Users/glenn/src/obspy_ext/antelope")
#import core

# Stuff in an Antelope-python example
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Antelope stuff
import antelope.datascope as datascope

# numpy & matplotlib
import numpy as np
#import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
#import pylab

# END OF GT ANTELOPE-OBSPY HEADER
#################################
x = np.arange(1,5)
plt.plot(x, x*1.5, label='Normal')
plt.plot(x, x*3.0, label='Fast')
plt.plot(x, x*1.5, label='Slow')
# What are the axis limits?
plt.axis()
# Set the axis limits, can also set with plt.xlim([xmin, xmax]) or plt.axis(xmin=XMIN, ...) to change one or many limits at a tme
plt.axis([0, 5, -1, 13])
# Add a grid
plt.grid(True)
# Add titles and labels
plt.title('A simple MPL plot')
plt.xlabel('X label')
plt.xlabel('Y label')
plt.legend(loc='upper left')
# Save it
plt.savefig('plot123.png')
