# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 10:55:19 2013

@author: Grahesh Parkar
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
import requests

class EventAnalysis():

    # initializes all values from config file.

    def __init__(self, configData, eventDetailsData):

        # eventDetails Data Format
##        [[u'Flag', u'Stock_Symbol', u'Q1_2012', u'Q2_2012', u'Q3_2012', u'Q4_2012'],
##        [u'Y', u'ABIRLANUV.NS', u'2012-02-13', u'2012-05-18', u'2012-08-06', u'2012-11-08'],
##        [u'Y', u'ACC.NS', u'2012-02-10', u'2012-05-10', u'2012-07-26', u'2012-10-18'],
##        [u'Y', u'ADANIENT.NS', u'2012-02-09', u'2012-05-25', u'2012-08-10', u'2012-10-25'],
##        [u'Y', u'ADANIPORT.NS', u'2012-02-06', u'2012-05-16', u'2012-08-10', u'2012-10-22'],
##        [u'Y', u'AMBUJACEM.NS', u'2012-02-10', u'2012-05-14', u'2012-07-26', u'2012-10-18']]

        # configData format
##        {u'End_Date': u'2012-12-31', u'Benchmark': u'NSE100', u'LookBack_Days': u'10',
##         u'File_Link': u'0AjoNUMfP67sMdDA4RjQ0Y3BDSDJzdFoyU19Qa1pkbWc',
##         u'Start_Date': u'2012-01-01', u'LookForward_Days': u'10'}

        date=configData['Start_Date'].split('-')
        self.startday=dt.datetime(int(date[0]),int(date[1]),int(date[2]))

        date=configData['End_Date'].split('-')
        self.endday=dt.datetime(int(date[0]),int(date[1]),int(date[2]))

        self.eventDetailsData=eventDetailsData
        self.lookBackDays=int(configData['LookBack_Days'])
        self.lookForwardDays=int(configData['LookForward_Days'])
        self.marketSymbol=configData['Benchmark']
        self.columns=configData['Columns']
        self.closefield = "close"
        self.saveFileName=configData['Save_File_Name']

        self.marketValueChange=configData['Market_Change']
        self.stockValueChange=configData['Stock_Change']

        self.marketChangeMin=configData['Market_Change_Min']
        self.marketChangeMax=configData['Market_Change_Max']
        self.stockChangeMin=configData['Stock_Change_Min']
        self.stockChangeMax=configData['Stock_Change_Max']

        self.noColumns=False

        if(self.columns[0] == 'NA'):
            self.noColumns=True


# formats the stock details file data into array of stock names and dates to be analyzed format
    def getDates(self, eventData, NSEtimestamps, columnIndexes):
        modifiedDates=[]
        for row in range(1, len(eventData)):
            tempData=[]
            if(eventData[row][0]=="Y"):
                tempData.append(eventData[row][1])

                if(self.noColumns): # if only stock names without mentioned dates needs to be analyzed
                    for time in NSEtimestamps:
                        tempData.append(time)

                else:
                    for i in range(2,len(eventData[row])): # if stock names on specified dates needs to be analyzed
                        if(eventData[row].index(eventData[row][i]) in columnIndexes):
                            y=eventData[row][i].split('-')
                            newDate=dt.datetime(int(y[0]),int(y[1]),int(y[2]))+dt.timedelta(hours=16)
                            if(newDate not in NSEtimestamps):
                                newDate=du.getNextNNSEdays(newDate,1,dt.timedelta(hours=16))
                            tempData.append(newDate)

                modifiedDates.append(tempData)

        return modifiedDates


# gets stock symbols that needs to be analyzed mentioned in stock details file.
    def getSymbols(self):
        eventData=self.eventDetailsData
        symbols=[]
        symbols.append(self.marketSymbol)
        for row in range(1, len(eventData)):
            if(eventData[row][0]=="Y"):
                symbols.append(eventData[row][1])
        return symbols


# creates event matrix when conditions (eg. fall in stock price or fall in market) is given.
    def getValueChangeMatrix(self, stockDates, NSEValues, mktneutDM, eventMatrix):
        if(self.marketValueChange!='NA'):
            if(self.marketValueChange[0]=='<'):
                if(self.stockValueChange!='NA'):
                    if(self.stockValueChange[0]=='<'):
                         for stock in stockDates:
                            stockName=stock[0]
                            for i in range(1,len(stock)):
                                if NSEValues[stock[i]] < float(self.marketValueChange[1:]) and mktneutDM[stockName][stock[i]] < float(self.stockValueChange[1:]) :
                                    eventMatrix[stockName][stock[i]] = 1.0  #overwriting by the bit, marking the event

                    else:
                        for stock in stockDates:
                            stockName=stock[0]
                            for i in range(1,len(stock)):
                                if NSEValues[stock[i]] < float(self.marketValueChange[1:]) and mktneutDM[stockName][stock[i]] > float(self.stockValueChange[1:]) :
                                    eventMatrix[stockName][stock[i]] = 1.0  #overwriting by the bit, marking the event
                else:
                    for stock in stockDates:
                        stockName=stock[0]
                        for i in range(1,len(stock)):
                            if NSEValues[stock[i]] < float(self.marketValueChange[1:]):
                                eventMatrix[stockName][stock[i]] = 1.0  #overwriting by the bit, marking the event

            else:
                if(self.stockValueChange!='NA'):
                    if(self.stockValueChange[0]=='<'):
                         for stock in stockDates:
                            stockName=stock[0]
                            for i in range(1,len(stock)):
                                if NSEValues[stock[i]] > float(self.marketValueChange[1:]) and mktneutDM[stockName][stock[i]] < float(self.stockValueChange[1:]) :
                                    eventMatrix[stockName][stock[i]] = 1.0  #overwriting by the bit, marking the event

                    else:
                        for stock in stockDates:
                            stockName=stock[0]
                            for i in range(1,len(stock)):
                                if NSEValues[stock[i]] > float(self.marketValueChange[1:]) and mktneutDM[stockName][stock[i]] > float(self.stockValueChange[1:]) :
                                    eventMatrix[stockName][stock[i]] = 1.0  #overwriting by the bit, marking the event
                else:
                    for stock in stockDates:
                        stockName=stock[0]
                        for i in range(1,len(stock)):
                            if NSEValues[stock[i]] > float(self.marketValueChange[1:]):
                                eventMatrix[stockName][stock[i]] = 1.0  #overwriting by the bit, marking the event

        return eventMatrix



# creates event matrix when range of condition (eg. fall in stock price in range of 2 numbers is given)
    def getRangeChangeMatrix(self, stockDates, NSEValues, mktneutDM, eventMatrix):
        if(self.marketChangeMin!='NA' and self.marketChangeMax!='NA' and self.stockChangeMin!='NA' and self.stockChangeMax!='NA'):
            for stock in stockDates:
                stockName=stock[0]
                for i in range(1,len(stock)):
                    if NSEValues[stock[i]] < float(self.marketChangeMax) and NSEValues[stock[i]] > float(self.marketChangeMin) and mktneutDM[stockName][stock[i]] < float(self.stockChangeMax) and mktneutDM[stockName][stock[i]] > float(self.stockChangeMin) :
                        eventMatrix[stockName][stock[i]] = 1.0  #overwriting by the bit, marking the event

        elif(self.marketChangeMin!='NA' and self.marketChangeMax!='NA'):
            for stock in stockDates:
                stockName=stock[0]
                for i in range(1,len(stock)):
                    if NSEValues[stock[i]] < float(self.marketChangeMax) and NSEValues[stock[i]] > float(self.marketChangeMin):
                        eventMatrix[stockName][stock[i]] = 1.0  #overwriting by the bit, marking the event
        else:
            for stock in stockDates:
                stockName=stock[0]
                for i in range(1,len(stock)):
                    if mktneutDM[stockName][stock[i]] < float(self.stockChangeMax) and mktneutDM[stockName][stock[i]] > float(self.stockChangeMin) :
                        eventMatrix[stockName][stock[i]] = 1.0  #overwriting by the bit, marking the event

        return eventMatrix



# gets the initial values that are required to calculate event matrix
    def findEvents(self, symbols, columnIndexes, verbose=False):

        eventDetails=self.eventDetailsData

        # Reading the Data for the list of Symbols.
        timeofday=dt.timedelta(hours=16)

        timestamps = du.getNSEdays(self.startday,self.endday,timeofday)

        stockDates=self.getDates(eventDetails, timestamps, columnIndexes)

        dataobj = da.DataAccess('NSEData')
        if verbose:
            print __name__ + " reading data"
        # Reading the Data

        close = dataobj.get_data(timestamps, symbols, self.closefield)

        #Completing the Data - Removing the NaN values from the Matrix
        close = (close.fillna(method='ffill')).fillna(method='backfill')


        # Calculating Daily Returns for the Market
        tsu.returnize0(close.values)
        NSEValues=close[self.marketSymbol]

        # Calculating the Returns of the Stock Relative to the Market
        # So if a Stock went up 5% and the Market rised 3%. The the return relative to market is 2%
        mktneutDM = close - close[self.marketSymbol]
        np_eventmat = copy.deepcopy(mktneutDM)


        for sym in symbols:
                for time in timestamps:
                        np_eventmat[sym][time]=np.NAN

        if verbose:
            print __name__ + " finding events"

        # Generating the Event Matrix
        # Event described is : Analysing Stock Prices before and after the occurence of an event.
        # Stocks are analysed on specific dates as per data provided in csv files accessed from Google Docs.

        if((self.marketChangeMin!='NA' and self.marketChangeMax!='NA') or (self.stockChangeMin!='NA' and self.stockChangeMax!='NA')):
            np_eventmat=self.getRangeChangeMatrix(stockDates, NSEValues, mktneutDM, np_eventmat)

        elif(self.marketValueChange!='NA' or self.stockValueChange!='NA'):
            np_eventmat=self.getValueChangeMatrix(stockDates, NSEValues, mktneutDM, np_eventmat)

# creates event matrix when no condition is given.
        else:
            for stock in stockDates:
                stockName=stock[0]
                for i in range(1,len(stock)):
                    np_eventmat[stockName][stock[i]] = 1.0  #overwriting by the bit, marking the event

        return np_eventmat



# gets indexes of columns from stock details file that needs to be analyzed
    def getColumnIndexes(self):
        columnidx=[]
        if(self.columns[0]=='ALL'):
            for col in range(2,len(self.eventDetailsData[0])):
                columnidx.append(self.eventDetailsData[0].index(self.eventDetailsData[0][col]))
        else:
            for col in self.columns:
                if(col in self.eventDetailsData[0]):
                    columnidx.append(self.eventDetailsData[0].index(col))

        return columnidx



# main function to analyze events
    def AnalyseEvents(self):

        columnIndexes=self.getColumnIndexes()

        stockSymbols=self.getSymbols()

        eventMatrix=self.findEvents(stockSymbols, columnIndexes, verbose=True)

        eventMatrix.to_csv(self.saveFileName+'_Event_Matrix'+'.csv', sep=',') # creates Event Matrix and saves as csv file
        eventProfiler = ep.EventProfiler(eventMatrix,self.startday,self.endday,self.lookBackDays,self.lookForwardDays,verbose=True)

        eventProfiler.study(self.saveFileName+".jpg",plotErrorBars=True,plotMarketNeutral=True,plotEvents=False,marketSymbol=self.marketSymbol)




