'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Dec, 25, 2012

@author: Grahesh Parkar
@summary: Simple Plots To Analyse Stocks from NSE INDIA
'''

import qstkutil.qsdateutil as du
import qstkutil.tsutil as tsu
import qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
from pylab import *
import pandas

print pandas.__version__

#
# Prepare to read the data
#
symbols = ["NSE","ABB.NS","ACC.NS","TCS.NS"]
startday = dt.datetime(2008,1,1)
endday = dt.datetime(2011,12,31)
timeofday=dt.timedelta(hours=16)
timestamps = du.getNYSEdays(startday,endday,timeofday)

#dataobj = da.DataAccess('Yahoo')

dataobj = da.DataAccess('NSEData')

voldata = dataobj.get_data(timestamps, symbols, "volume",verbose=True)
close = dataobj.get_data(timestamps, symbols, "close",verbose=True)
actualclose = dataobj.get_data(timestamps, symbols, "actual_close",verbose=True)
#
# Plot the adjusted close data
#
plt.clf()
newtimestamps = close.index
pricedat = close.values # pull the 2D ndarray out of the pandas object
plt.plot(newtimestamps,pricedat)
plt.legend(symbols)
plt.ylabel('Adjusted Close')
plt.xlabel('Date')
savefig('Adjusted_Close.jpg',format='jpg')

#
# Plot the normalized closing data
#
plt.clf()
normdat = pricedat/pricedat[0,:]
plt.plot(newtimestamps,normdat)
plt.legend(symbols)
plt.ylabel('Normalized Close')
plt.xlabel('Date')
savefig('Normalized.jpg',format='jpg')

##
## Plot daily returns
##
plt.clf()
plt.cla()
tsu.returnize0(normdat)
plt.plot(newtimestamps[0:50],normdat[0:50,0]) # $NSE 50 days
plt.plot(newtimestamps[0:50],normdat[0:50,1]) # TCS 50 days
plt.axhline(y=0,color='r')
plt.legend(['$NSE','TCS'])
plt.ylabel('Daily Returns')
plt.xlabel('Date')
savefig('Daily_Returns.jpg',format='jpg')

##
## Scatter plot
##
plt.clf()
plt.cla()
plt.scatter(normdat[:,0],normdat[:,1],c='blue') # $NSE v TCS
plt.ylabel('TCS')
plt.xlabel('$NSE')
savefig('Scatter_NSEvTCS.jpg',format='jpg')


print "done"
