from obspy.core import read
st = read('http://examples.obspy.org/RJOB_061005_072159.ehz.new')
print st
st[0].stats.station
st[0].stats.gse2.datatype
st[0].data
len(st[0])
st[0].plot(color='k')

