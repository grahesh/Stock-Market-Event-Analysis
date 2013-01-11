# -*- coding: utf-8 -*-
"""
Created on Tue Jan 01 18:21:19 2013

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

# Get the data from the data store
storename = "NSEData" # get data from our daily prices source
# Available field names: open, close, high, low, close, actual_close, volume
closefield = "close"
volumefield = "volume"
window = 10

def getSymbols(data):
    symbols=[]
    for x in data:
        result=x.split(',')
        if(result[0]=="YES"):
            symbols.append(result[1])
    return symbols        

def getDates(data):
    modifiedDates=[]
    
    for x in data:        
        tempData=[]
        result=x.split(',')
        
        if(result[0]=="YES"):
            tempData.append(result[1]) 
            
            for i in range(2,len(result)):
                y=result[i].split('-')
                tempData.append(dt.datetime(int(y[0]),int(y[1]),int(y[2]))+dt.timedelta(hours=16))
            modifiedDates.append(tempData)
            
    return modifiedDates        
        
        

def findEvents(data, startday,endday, marketSymbol,verbose=False):

        # Reading the Data for the list of Symbols.     
        timeofday=dt.timedelta(hours=16)
        timestamps = du.getNYSEdays(startday,endday,timeofday)
        
        dataobj = da.DataAccess('NSEData')
        if verbose:
            print __name__ + " reading data"
        # Reading the Data
        symbols=getSymbols(data)
        
        eventDetails=getDates(data)
        
        close = dataobj.get_data(timestamps, symbols, closefield)   
        
        #Completing the Data - Removing the NaN values from the Matrix
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
        # Event described is : Analysing Stock Prices before and after the occurence of an event.
        # Stocks are analysed on specific dates as per data provided in csv files.

        for stock in eventDetails:      
            stockName=stock[0]
                        
            for i in range(1,len(stock)):
                np_eventmat[stockName][stock[i]] = 1.0  #overwriting by the bit, marking the event
     
                        
        return np_eventmat
 


#################################################
################ MAIN CODE ######################
#################################################


startday = dt.datetime(2012,1,1)
endday = dt.datetime(2012,12,30)


data = np.loadtxt('NSEport.csv',dtype=str,comments='#', skiprows=1)

eventMatrix = findEvents(data,startday,endday,marketSymbol='NSE',verbose=True)
eventMatrix.to_csv('eventmatrix.csv', sep=',')
eventProfiler = ep.EventProfiler(eventMatrix,startday,endday,lookback_days=10,lookforward_days=10,verbose=True)

eventProfiler.study(filename="EventAnalysisOutput.jpg",plotErrorBars=True,plotMarketNeutral=True,plotEvents=False,marketSymbol='NSE')





