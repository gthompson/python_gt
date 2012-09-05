#!/Library/Frameworks/Python.framework/Versions/2.6/bin/python
import pylab
#import converttime
import os
outfile = '/usr/local/mosaic/AVO/internal/avoseis/dev/plots/testplot.png'
if os.path.exists(outfile):
	os.remove(outfile)
#t = converttime.utnow()
x = pylab.randn(10000)
pylab.hist(x, 100)
#pylab.xlabel('updated at %d',t)
pylab.savefig(outfile)
