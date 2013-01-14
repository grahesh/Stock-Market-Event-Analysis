# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 10:55:19 2013

@author: Grahesh and Ashwin
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
import gspread

# Get the data from the data store
storename = "NSEData" # get data from our daily prices source
# Available field names: open, close, high, low, close, actual_close, volume
closefield = "close"
volumefield = "volume"
window = 10

def getSymbols(data, marketSymbol):
    symbols=[]
    symbols.append(marketSymbol)
    for row in range(1, len(data)):
        if(data[row][0]=="YES"):
            symbols.append(data[row][1])
    return symbols        

def getDates(data):
    modifiedDates=[]
    
    for row in range(1, len(data)):        
        tempData=[]
        
        if(data[row][0]=="YES"):
            tempData.append(data[row][1]) 
            
            for i in range(2,len(data[row])):
                y=data[row][i].split('/')
                tempData.append(dt.datetime(int(y[2]),int(y[0]),int(y[1]))+dt.timedelta(hours=16))
            modifiedDates.append(tempData)
    
                
    return modifiedDates        
        
        

def findEvents(data, startday,endday, marketSymbol,verbose=False):

        # Reading the Data for the list of Symbols.     
        timeofday=dt.timedelta(hours=16)
        timestamps = du.getNSEdays(startday,endday,timeofday)
        
        dataobj = da.DataAccess('NSEData')
        if verbose:
            print __name__ + " reading data"
        # Reading the Data
        symbols=getSymbols(data, marketSymbol)
        
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
        # Stocks are analysed on specific dates as per data provided in csv files accessed from Google Docs.

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

# Data Representation as per in google spreadsheet

#data=[['Read', 'symbol', 'Date1', 'Date2'],
#      ['YES', 'NSE', '9/27/2012', '8/17/2012'],
#      ['NO', 'TCS.NS', '9/28/2012', '8/21/2012'],
#      ['YES', 'ABB.NS', '9/27/2012', '8/17/2012'],
#      ['YES', 'ACC.NS', '9/26/2012', '8/16/2012']]


# code ot access spreadsheet in google docs
gc = gspread.login('stockeventstudy@gmail.com','stockmarketevent')

sheetData = gc.open("NSEport").sheet1

data = sheetData.get_all_values()
# code to access sreadsheet in google docs


eventMatrix = findEvents(data,startday,endday,marketSymbol='NSE',verbose=True)
eventMatrix.to_csv('eventmatrix.csv', sep=',')
eventProfiler = ep.EventProfiler(eventMatrix,startday,endday,lookback_days=10,lookforward_days=10,verbose=True)

eventProfiler.study(filename="EventAnalysisOutput.jpg",plotErrorBars=True,plotMarketNeutral=True,plotEvents=False,marketSymbol='NSE')





