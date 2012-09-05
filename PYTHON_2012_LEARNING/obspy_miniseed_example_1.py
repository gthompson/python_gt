#!/opt/antelope/python2.7.2-64/bin/python
###############################
#a GT ANTELOPE OBSPY HEADER
import sys, os
sys.path.append(os.environ['ANTELOPE'] + "/data/python")

# OBSPY_EXT by Mark Williams
sys.path.append("/Users/glenn/src/obspy_ext/antelope")
import core

# Stuff in an Antelope-python example
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Antelope stuff
import antelope.datascope as datascope

# numpy & matplotlib
import numpy as np
#import matplotlib.mlab as mlab
#import matplotlib.pyplot as plt
import pylab

# END OF GT ANTELOPE-OBSPY HEADER
#################################

# obspy_ext (Antelope-ObsPy) example:
from obspy.core import UTCDateTime
st = core.readANTELOPE('RDtest1', station='REF', channel='EHZ', \
starttime=UTCDateTime(2009,3,23), endtime=UTCDateTime(2009,3,24))
print st

# basic local miniseed example
from obspy.core import read
st = read('/Users/glenn/benchmark_antelope/db/2009/082/REF.EHZ.2009:082:00:00:00')
st
print st
print (st[0].stats)
st.write('REF.EHZ.2009:082.mseed', format='MSEED')
#st.write('REF.EHZ.2009:082.wave', format='WAV', framerate=6000)
st.write('REF.EHZ.2009:082.sac', format='SAC')

# This needs basemap and demonstrates the event and catalog classes
from obspy.core.event import *
cat = readEvents(\
"http://www.seismicportal.eu/services/event/search?magMin=8.0")
cat.plot()



# IRIS DMC example
from obspy.iris import Client
from obspy.core import UTCDateTime
client = Client()
t = UTCDateTime("2012-08-05T06:00:00.000")
st = client.getWaveform('IU', 'ANMO', '00', 'BHZ', t, t + 300)
st.plot()

# Earthworm wave server example - connection is refused though
from obspy.earthworm import Client
client = Client("pele.ess.washington.edu", 16017)
response = client.availability("UW", "TUCA", channel="BHZ")
print response
t = response[0][4]
st = client.getWaveform('UW', 'TUCA', '', 'BH*', t + 100, t + 130)
st.plot()

