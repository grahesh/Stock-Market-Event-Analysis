# -*- coding: utf-8 -*-
"""
Created on Thu Jan 03 10:16:39 2013

@author: Grahesh
"""

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

def getMonthEndDates(timestamps):
        newTS=[]
        temp=timestamps[0].month
        
        for x in range(0, len(timestamps)-1):
            if(temp!=timestamps[x].month):
                newTS.append(timestamps[x-1])
                temp=timestamps[x].month
        
        newTS.append(timestamps[len(timestamps)-1])
        
        return newTS

def getQuarterEndDates(timestamps):
        newTS=[]
        
        monthEndDates=getMonthEndDates(timestamps)
               
        for x in range(0, len(monthEndDates)-1):
            if(monthEndDates[x].month==3 or monthEndDates[x].month==6 or monthEndDates[x].month==9 or monthEndDates[x].month==12):
                newTS.append(monthEndDates[x])            
        
        return newTS
        

def findEvents(symbols, startday,endday, marketSymbol,verbose=False):

        # Reading the Data for the list of Symbols.     
        timeofday=dt.timedelta(hours=16)
        timestamps = du.getNYSEdays(startday,endday,timeofday)


        endOfQuarter=getQuarterEndDates(timestamps)
         
     
        dataobj = da.DataAccess('NSEData')
        if verbose:
            print __name__ + " reading data"
        # Reading the Data
        
        close = dataobj.get_data(timestamps, symbols, closefield)

        # Completing the Data - Removing the NaN values from the Matrix
        close = (close.fillna(method='ffill')).fillna(method='backfill')

        
        # Calculating Daily Returns for the Market
        tsu.returnize0(close.values)


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
        # Event described is : Analysis Quarter End prices of stocks

        for symbol in symbols:
                for i in endOfQuarter:                       

                        np_eventmat[symbol][i] = 1.0  #overwriting by the bit, marking the event
     
                        
        return np_eventmat


#################################################
################ MAIN CODE ######################
#################################################


symbols = np.loadtxt('NSE500port.csv',dtype='S13',comments='#', skiprows=1)
# You might get a message about some files being missing, don't worry about it.

#symbols =['SPY','BFRE','ATCS','RSERF','GDNEF','LAST','ATTUF','JBFCF','CYVA','SPF','XPO','EHECF','TEMO','AOLS','CSNT','REMI','GLRP','AIFLY','BEE','DJRT','CHSTF','AICAF']
#symbols=['NSE','3MINDIA.NS','AARTIIND.NS','ABAN.NS','ABB.NS','ABGSHIP.NS','ABIRLANUV.NS','ACC.NS','ADANIENT.NS','ADANIPORT.NS','ADANIPOWE.NS','ADVANTA.NS','ALLCARGO.NS','AIAENG.NS','AIL.NS','AZKOINDIA.NS']


startday = dt.datetime(2011,1,1)
endday = dt.datetime(2012,1,1)
eventMatrix = findEvents(symbols,startday,endday,marketSymbol='NSE500',verbose=True)

eventMatrix.to_csv('eventmatrix.csv', sep=',')

eventProfiler = ep.EventProfiler(eventMatrix,startday,endday,lookback_days=20,lookforward_days=20,verbose=True)

eventProfiler.study(filename="QuarterEndEventStudy.jpg",plotErrorBars=True,plotMarketNeutral=True,plotEvents=False,marketSymbol='NSE500')


