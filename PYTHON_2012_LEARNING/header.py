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

