# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 10:55:19 2013

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
import qstkstudy.Event_Analysis as ea
import requests
import csv
import time


def findEvents(symbols, startday,endday,weeks, marketSymbol,verbose=False):

        # week calc
        week=dt.timedelta(weeks=weeks)
        time = startday.time()
        lookbackday=dt.datetime.combine(startday,time)-week
        # week cal

        # Reading the Data for the list of Symbols.
        timeofday=dt.timedelta(hours=16)

        closefield = "close"
        highfield = "high"
        lowfield='low'
        lookbackTimestamps = du.getNSEdays(lookbackday,startday,timeofday)
        analyzeTimestamps=du.getNSEdays(startday,endday,timeofday)
        timestamps=lookbackTimestamps+analyzeTimestamps

        np_eventmat=pandas.DataFrame(index=timestamps, columns=symbols)

        dataobj = da.DataAccess('NSEData')

        close = dataobj.get_data(timestamps, symbols, closefield)
        close = (close.fillna(method='ffill')).fillna(method='backfill')

        high = dataobj.get_data(timestamps, symbols, highfield)
        high = (high.fillna(method='ffill')).fillna(method='backfill')

        low = dataobj.get_data(timestamps, symbols, lowfield)
        low = (low.fillna(method='ffill')).fillna(method='backfill')

##        close.to_csv('res.csv',sep=',')

        for i in range(0, len(analyzeTimestamps)):
            print 'Iteration : ',i+1
            currentDates = [close.index[j] for j in range(i,len(lookbackTimestamps)+1+i)]

            subDataframe=close.ix[currentDates]
            highDataframe=high.ix[currentDates]
            lowDataframe=low.ix[currentDates]

            eventDate= currentDates[len(currentDates)-1]

##            maxValue=subDataframe.idxmax()
##            minValue=subDataframe.idxmin()

            highValue=highDataframe.idxmax()
            lowValue=lowDataframe.idxmin()

            for stockname, date in highValue.T.iteritems():
                value=(close[stockname][eventDate]/high[stockname][date])-1
                if(value<=0.00 and value>-0.02):
                    np_eventmat[stockname][eventDate]='52wk+++,'+str(close[stockname][eventDate])+','+str(high[stockname][date])+','+str(date.date())+','+str(value*100)+','+str(currentDates[0].date())+' - '+str(eventDate.date())
                elif(value<-0.02 and value>-0.05):
                    np_eventmat[stockname][eventDate]='52wk++,'+str(close[stockname][eventDate])+','+str(high[stockname][date])+','+str(date.date())+','+str(value*100)+','+str(currentDates[0].date())+' - '+str(eventDate.date())
                elif(value<-0.05 and value>-0.07):
                    np_eventmat[stockname][eventDate]='52wk+,'+str(close[stockname][eventDate])+','+str(high[stockname][date])+','+str(date.date())+','+str(value*100)+','+str(currentDates[0].date())+' - '+str(eventDate.date())


            for stockname, date in lowValue.T.iteritems():
                value=(close[stockname][eventDate]/low[stockname][date])-1
                if(value>=0.00 and value<0.02):
                    np_eventmat[stockname][eventDate]='52wk---,'+str(close[stockname][eventDate])+','+str(low[stockname][date])+','+str(date.date())+','+str(value*100)+','+str(currentDates[0].date())+' - '+str(eventDate.date())
                elif(value>0.02 and value<0.05):
                    np_eventmat[stockname][eventDate]='52wk--,'+str(close[stockname][eventDate])+','+str(low[stockname][date])+','+str(date.date())+','+str(value*100)+','+str(currentDates[0].date())+' - '+str(eventDate.date())
                elif(value>0.05 and value<0.07):
                    np_eventmat[stockname][eventDate]='52wk-,'+str(close[stockname][eventDate])+','+str(low[stockname][date])+','+str(date.date())+','+str(value*100)+','+str(currentDates[0].date())+' - '+str(eventDate.date())

        return np_eventmat


#################################################
################ MAIN CODE ######################
#################################################

##start_time = time.time()

symbols = np.loadtxt('NSE100port.csv',dtype=str,comments='#', skiprows=1)

startday = dt.datetime(2013,1,30)
endday = dt.datetime(2013,1,31)
weeks=52
eventMatrix = findEvents(symbols,startday,endday,weeks,marketSymbol='NSE100',verbose=True)
##eventMatrix.to_csv('eventmat.csv',sep=',')

##print time.time() - start_time, "seconds"

#Signals File
outputFile=open('Signals.csv','wb')
cot=csv.writer(outputFile)
cot.writerow(['EVENT DATE','STOCK','SIGNAL','EVENT DATE PRICE','HIGH/LOW PRICE','HIGH/LOW DATE','% CHANGE', 'ANALYSIS RANGE'])
for stockname,details in eventMatrix.iterkv():
    for date, row in details.T.iteritems():
        if(str((row)).lower() != 'nan'):
            data=row.split(',')
            cot.writerow([date.date(),stockname,data[0],data[1],data[2],data[3],data[4],data[5]])
outputFile.close()


#Data File for analysis
##outputFile=open('configData.csv','wb')
##cot=csv.writer(outputFile)
##for stockname,details in eventMatrix.iterkv():
##    out=[]
##    out.append(stockname)
##    for date,value in details.iterkv():
##        if(value==1.0):
##            out.append(date.date())
##    cot.writerow(out)
##outputFile.close()

##print time.time() - start_time, "seconds"

##eventProfiler = ep.EventProfiler(eventMatrix,startday,endday,lookback_days=4,lookforward_days=4,verbose=True)
##
##eventProfiler.study(filename="52wkHighHits.jpg",plotErrorBars=True,plotMarketNeutral=True,plotEvents=False,marketSymbol='NSE100')
