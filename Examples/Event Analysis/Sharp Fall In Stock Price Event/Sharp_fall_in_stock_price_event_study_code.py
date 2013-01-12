'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Dec, 25, 2012

@author: Grahesh
@summary: Price Dropping Event Study
'''


import pandas 
from qstkutil import DataAccess as da
import numpy as np
import math
import copy
import qstkutil.qsdateutil as du
import datetime as dt
import qstkutil.DataAccess as da
import qstkutil.tsutil as tsu
import qstkstudy.EventProfiler as ep

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""

# Get the data from the data store
storename = "NSEData" # get data from our daily prices source
# Available field names: open, close, high, low, close, actual_close, volume
closefield = "close"
volumefield = "volume"
window = 10

def findEvents(symbols, startday,endday, marketSymbol,verbose=False):

	# Reading the Data for the list of Symbols.	
	timeofday=dt.timedelta(hours=16)
	timestamps = du.getNSEdays(startday,endday,timeofday)
	dataobj = da.DataAccess('NSEData')
	if verbose:
            print __name__ + " reading data"
	# Reading the Data
	close = dataobj.get_data(timestamps, symbols, closefield)
	
	# Completing the Data - Removing the NaN values from the Matrix
	close = (close.fillna(method='ffill')).fillna(method='backfill')

	
	# Calculating Daily Returns for the Market
	tsu.returnize0(close.values)
	SPYValues=close[marketSymbol]

	# Calculating the Returns of the Stock Relative to the Market 
	# So if a Stock went up 5% and the Market rised 3%. The the return relative to market is 2% 
	mktneutDM = close - close[marketSymbol] 

	np_eventmat = copy.deepcopy(mktneutDM)
	for sym in symbols:
		for time in timestamps:
			np_eventmat[sym][time]=np.NAN

	if verbose:
            print __name__ + " finding events"

	# Generating the Event Matrix
	# Event described is : Analysis of events occuring when stock price falls to a certain value

	for symbol in symbols:
		
	    for i in range(1,len(mktneutDM[symbol])):
	        if SPYValues[i]<-0.01 and mktneutDM[symbol][i] < -0.02 : # When market fall is more than 3% and also the stock compared to market is also fell by more than 5%.
             		np_eventmat[symbol][i] = 1.0  #overwriting by the bit, marking the event
			
	return np_eventmat


#################################################
################ MAIN CODE ######################
#################################################


symbols = np.loadtxt('NSE500port.csv',dtype='S13',comments='#', skiprows=1)

# You might get a message about some files being missing, don't worry about it.
#symbols=['NSE','3MINDIA.NS','AARTIIND.NS','ABAN.NS','ABB.NS','ABGSHIP.NS','ABIRLANUV.NS','ACC.NS','ADANIENT.NS','ADANIPORT.NS','ADANIPOWE.NS','ADVANTA.NS','ALLCARGO.NS','AIAENG.NS','AIL.NS','AZKOINDIA.NS']
#symbols =['BFRE','ATCS','RSERF','GDNEF','LAST','ATTUF','JBFCF','CYVA','SPF','XPO','EHECF','TEMO','AOLS','CSNT','REMI','GLRP','AIFLY','BEE','DJRT','CHSTF','AICAF']


startday = dt.datetime(2011,1,1)
endday = dt.datetime(2012,1,1)
eventMatrix = findEvents(symbols,startday,endday,marketSymbol='NSE500',verbose=True)
eventMatrix.to_csv('eventmatrix.csv', sep=',')
eventProfiler = ep.EventProfiler(eventMatrix,startday,endday,lookback_days=20,lookforward_days=20,verbose=True)

eventProfiler.study(filename="SharpFallInStockPriceEventStudy.jpg",plotErrorBars=True,plotMarketNeutral=True,plotEvents=False,marketSymbol='NSE500')


